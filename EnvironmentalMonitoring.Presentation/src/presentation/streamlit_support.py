"""Funções de suporte para a interface Streamlit.

Este módulo contém todas as funções auxiliares para a aplicação de
Monitoramento Ambiental, incluindo carregamento de dados, validação,
processamento de pipeline e renderização de componentes.
"""

from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4
import json

import streamlit as st

from src.database.reading_repository import ReadingRepository
from src.analytics.service import AnalyticsService
from src.models.statistics_result import StatisticsResult
from src.reporting import (
    export_statistics_to_csv,
    export_statistics_with_outliers_detail,
)
from src.security.log_utils import tratar_erro
from src.processing.bronze_contract_validator import validate_contract
from src.processing.json_to_parquet import json_to_parquet
from src.config import logger
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.blob_storage_service import BlobStorageService
from src.ingestion.data_parser import DataParser
from src.ingestion.api_client import APIClient
from src.constants import SERVICES
from src.models import Station
from src.models.reading import Reading

# ============================================================================
# CARREGAMENTO DE SCHEMAS BRONZE
# ============================================================================

def _load_schema(schema_name: str) -> dict:
    """Carrega um schema JSON do diretório de contratos.
    
    Args:
        schema_name: Nome do arquivo schema (ex: weather-bronze.schema.json)
    
    Returns:
        dict: Schema carregado
    """
    schema_path = Path(__file__).parent.parent.parent / "contracts" / "schemas" / schema_name
    try:
        with open(schema_path, "r", encoding="utf-8") as schema_file:
            return json.load(schema_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        tratar_erro(
            e,
            f"Falha ao carregar schema {schema_name}",
            encerrar=False,
        )
        return {}

WEATHER_SCHEMA = _load_schema("weather-bronze.schema.json")
WATER_SCHEMA = _load_schema("water-bronze.schema.json")

# ============================================================================
# LOGGING DE AUDITORIA
# ============================================================================

def _log_backfill_to_audit(blob_name: str, category: str) -> None:
    """Registra um evento de substituição (backfill) de documento no arquivo de auditoria.
    
    Todos os eventos de backfill são agregados em um único arquivo JSONL
    (JSON Lines format), onde cada linha representa um evento.
    
    Args:
        blob_name: Nome do blob que foi atualizado/substituído.
        category: Categoria do documento (weather ou water).
    """
    try:
        audit_service = BlobStorageService(SERVICES["audit"]["blob_container"])
        
        event_id = str(uuid4())
        timestamp = datetime.now(timezone.utc)
        
        log_entry = {
            "event_id": event_id,
            "timestamp": timestamp.isoformat(),
            "event_type": "BACKFILL",
            "action": "DOCUMENT_UPDATED",
            "category": category,
            "blob_name": blob_name,
            "description": f"Documento {category} substituído durante ingestão"
        }
        
        audit_log_name = f"backfill_{category.lower()}.jsonl"
        audit_service.append_line_to_jsonl(audit_log_name, log_entry)
        
        logger.info(
            f"Log de backfill registrado",
            extra={
                "event_id": event_id,
                "event": "BACKFILL",
                "category": category,
                "blob_name": blob_name,
                "audit_log": audit_log_name
            }
        )
    except Exception as e:
        tratar_erro(
            e,
            f"Falha ao registrar log de backfill para {blob_name}",
            encerrar=False,
        )


def load_stations():
    """Carrega lista de estações do repositório.
    
    Returns:
        list: Lista de objetos Station do banco de dados.
    """
    try:
        repository = ReadingRepository()
        return repository.get_stations()
    except Exception as e:
        tratar_erro(
            e,
            "Falha ao carregar estações da interface Streamlit",
            encerrar=False,
        )
        return []


def validate_date_range(
    start_date_value: date,
    end_date_value: date,
) -> str | None:
    """Valida o intervalo de datas fornecido.
    
    Regras de validação:
    - Data final > data inicial
    - Datas diferentes
    - Data inicial <= 90 dias no passado
    - Data final <= ontem
    - Sem datas futuras
    
    Args:
        start_date_value: Data inicial (date)
        end_date_value: Data final (date)
    
    Returns:
        str | None: Mensagem de erro em português ou None se válido.
    """
    today = date.today()
    
    if start_date_value >= end_date_value:
        return "A data final deve ser maior que a data inicial."
    
    if start_date_value == end_date_value:
        return "As datas não podem ser iguais."
    
    max_days_back = today - timedelta(days=90)
    if start_date_value < max_days_back:
        return "A data inicial pode ser no máximo 90 dias anterior à data atual."
    
    if end_date_value >= today:
        return "A data final deve ser no máximo ontem."
    
    if end_date_value > today:
        return "Datas futuras não são permitidas."
    
    return None


def statistics_to_rows(
    statistics: list[StatisticsResult],
) -> list[dict[str, object]]:
    """Converte lista de StatisticsResult em linhas para exibição em tabela.
    
    Args:
        statistics: Lista de resultados estatísticos.
    
    Returns:
        list[dict]: Lista de dicionários com dados formatados para tabela.
    """
    return [
        {
            "Parâmetro": result.parameter_name or result.parameter_code,
            "Quantidade": result.count,
            "Média": f"{result.average:.2f}",
            "Mediana": f"{result.median:.2f}",
            "Desvio padrão": f"{result.standard_deviation:.2f}",
            "Q1": f"{result.q1:.2f}",
            "Q3": f"{result.q3:.2f}",
            "IQR": f"{result.iqr:.2f}",
            "Limite inferior": f"{result.lower_bound:.2f}",
            "Limite superior": f"{result.upper_bound:.2f}",
            "Quantidade de outliers": len(result.outliers),
        }
        for result in statistics
    ]


def read_file_bytes(file_path: str) -> bytes:
    """Lê conteúdo de arquivo em bytes.
    
    Args:
        file_path: Caminho do arquivo.
    
    Returns:
        bytes: Conteúdo do arquivo.
    """
    return Path(file_path).read_bytes()


def render_statistics_table(statistics: list[StatisticsResult]) -> None:
    """Renderiza tabela de estatísticas.
    
    Args:
        statistics: Lista de resultados estatísticos.
    """
    if not statistics:
        st.warning("Nenhuma estatística disponível.")
        return
    
    rows = statistics_to_rows(statistics)
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_download_buttons(
    csv_path: str | None,
    outliers_path: str | None,
    category: str,
) -> None:
    """Renderiza botões de download para arquivos CSV.
    
    Args:
        csv_path: Caminho do arquivo de estatísticas.
        outliers_path: Caminho do arquivo de outliers.
        category: Categoria (weather ou water) para identificação dos botões.
    """
    
    if csv_path and Path(csv_path).exists():
        file_content = read_file_bytes(csv_path)
        st.download_button(
            label="Baixar Estatísticas",
            data=file_content,
            file_name=Path(csv_path).name,
            mime="text/csv",
            key=f"download_statistics_{category}",
        )
    
    if outliers_path and Path(outliers_path).exists():
        file_content = read_file_bytes(outliers_path)
        st.download_button(
            label="Baixar Outliers",
            data=file_content,
            file_name=Path(outliers_path).name,
            mime="text/csv",
            key=f"download_outliers_{category}",
        )


def run_ingestion(
    api_client: APIClient,
    selected_station,
    start_date: datetime,
    end_date: datetime,
    weather_status,
    water_status,
) -> tuple[list, list]:
    """Executa ingestion de weather e water em paralelo.
    
    Args:
        api_client: Cliente da API para ingestão de dados.
        selected_station: Estação selecionada.
        start_date: Data inicial (datetime com UTC).
        end_date: Data final (datetime com UTC).
        weather_status: Placeholder para status de weather.
        water_status: Placeholder para status de water.
    
    Returns:
        tuple: (weather_readings, water_readings)
    """
    weather_readings_json_list = []
    water_readings_json_list = []
    weather_status.info("Meteorologia: consulta em andamento...")
    water_status.info("Qualidade da água: consulta em andamento...") 
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    api_client.fetch_readings,
                    selected_station,
                    start_date,
                    end_date,
                    SERVICES["weather"]["api_url_env"],
                ): "weather",
                executor.submit(
                    api_client.fetch_readings,
                    selected_station,
                    start_date,
                    end_date,
                    SERVICES["water"]["api_url_env"],
                ): "water",
            }
            
            for future in as_completed(futures):
                category = futures[future]
                readings_json_list = future.result()
                
                if category == "weather":
                    weather_readings_json_list = readings_json_list
                    weather_status.success(
                        f"Meteorologia: {len(weather_readings_json_list)} leitura(s) coletada(s)."
                    )
                elif category == "water":
                    water_readings_json_list = readings_json_list
                    water_status.success(
                        f"Qualidade da água: {len(water_readings_json_list)} leitura(s) coletada(s)."
                    )
    
    except Exception as e:
        weather_status.error("Falha na consulta meteorológica.")
        water_status.error("Falha na consulta de qualidade da água.")
        raise
    
    return weather_readings_json_list, water_readings_json_list

def parser_readings(
    repository: ReadingRepository,
    dataParser: DataParser,
    ingestion_datetime: datetime,
    station_metadata: dict,
    selected_station: Station,
    weather_readings_json_list: list[dict],
    water_readings_json_list: list[dict]
) -> tuple[list[Reading], list[dict], list[Reading], list[dict]]:
    """Faz o parsing das leituras meteorológicas e de qualidade da água
    
    Args:
        weather_readings_json_list: Leituras meteorológicas.
        water_readings_json_list: Leituras de qualidade da água.
    
    Returns:
        tuple: (readings_weather, documents_weather, readings_water, documents_water).
    """
    readings_weather, documents_weather = [], []
    readings_water, documents_water = [], []
    allowed_parameters_weather = repository.get_parameters_by_CategoryCode(SERVICES["weather"]["category_code"])
    operator_weather = repository.get_operator_by_service_code(SERVICES["weather"]["operator_code"])
    if operator_weather is None:
        raise ValueError("Operador do serviço de meteorologia não encontrado.")
    for weather_readings_json in weather_readings_json_list:
        if not weather_readings_json:
            continue
        metadata = {
            "contract_version": "1.0",
            "source": {"type": "api", "provider": "meersens"},
            "ingestion_datetime": ingestion_datetime,
            "station": station_metadata,
        }
        readings_weather_temp, documents_weather_temp = dataParser.build_documents_readings(SERVICES["weather"]["specifications_name"], weather_readings_json, metadata, selected_station.id, operator_weather, allowed_parameters_weather, SERVICES["weather"]["category_code"])
        readings_weather.extend(readings_weather_temp)
        documents_weather.extend(documents_weather_temp)

    allowed_parameters_water = repository.get_parameters_by_CategoryCode(SERVICES["water"]["category_code"])
    operator_water = repository.get_operator_by_service_code(SERVICES["water"]["operator_code"])
    if operator_water is None:
        raise ValueError("Operador do serviço de qualidade da água não encontrado.")
    for water_readings_json in water_readings_json_list:
        if not water_readings_json:
            continue
        metadata = {
            "contract_version": "1.0",
            "source": {"type": "api", "provider": "meersens"},
            "ingestion_datetime": ingestion_datetime,
            "station": station_metadata,
        }
        readings_water_temp, documents_water_temp = dataParser.build_documents_readings(SERVICES["water"]["specifications_name"], water_readings_json, metadata, selected_station.id, operator_water, allowed_parameters_water, SERVICES["water"]["category_code"])
        readings_water.extend(readings_water_temp)
        documents_water.extend(documents_water_temp)

    return readings_weather, documents_weather, readings_water, documents_water


def persist_readings_bronze(
    documents_weather: list[dict],
    documents_water: list[dict],
) -> tuple[tuple[int, int, list[dict]], tuple[int, int, list[dict]]]:
    """Persiste leituras no blob storage bronze.
    
    Valida cada documento contra seu respectivo contrato antes de persistir.
    Documentos inválidos não são persistidos. Registra logs de substituição.
    
    Args:
        documents_weather: Leituras meteorológicas.
        documents_water: Leituras de qualidade da água.
    
    Returns:
        tuple: ((weather_inserted, weather_updated, weather_persisted_docs), 
                (water_inserted, water_updated, water_persisted_docs)).
    """
    blob_service_weather = BlobStorageService(SERVICES["weather"]["blob_container"])
    blob_service_water = BlobStorageService(SERVICES["water"]["blob_container"])
    weather_inserted = 0
    weather_updated = 0
    water_inserted = 0
    water_updated = 0
    weather_persisted_docs = []
    water_persisted_docs = []

    for document in documents_weather:        
        is_valid, error = validate_contract(document["document"], WEATHER_SCHEMA)
        
        if not is_valid:
            # TODO: Gerar log de contrato inválido com detalhes do erro
            continue
        
        # Verifica se o blob já existe e armazena o documento bronze no serviço de armazenamento de blobs
        if blob_service_weather.blob_exists(document['blob_name']): 
            weather_updated += 1
            _log_backfill_to_audit(document['blob_name'], SERVICES["weather"]["category_code"])
        else:
            weather_inserted += 1
        blob_service_weather.upload_json(document['blob_name'], document["document"])
        weather_persisted_docs.append(document)

    for document in documents_water:        
        is_valid, error = validate_contract(document["document"], WATER_SCHEMA)
        
        if not is_valid:
            # TODO: Gerar log de contrato inválido com detalhes do erro
            continue
        
        # Verifica se o blob já existe e armazena o documento bronze no serviço de armazenamento de blobs
        if blob_service_water.blob_exists(document['blob_name']): 
            water_updated += 1
            _log_backfill_to_audit(document['blob_name'], SERVICES["water"]["category_code"])
        else:
            water_inserted += 1
        blob_service_water.upload_json(document['blob_name'], document["document"])
        water_persisted_docs.append(document)
    
    return (weather_inserted, weather_updated, weather_persisted_docs), (water_inserted, water_updated, water_persisted_docs)


def persist_readings_silver(
    parquet_docs_weather: list[dict],
    parquet_docs_water: list[dict],
) -> tuple[tuple[int, int, list[dict]], tuple[int, int, list[dict]]]:
    """Persiste leituras em Parquet no blob storage silver.
    
    Recebe documentos já convertidos para Parquet e os armazena no container
    silver seguindo o mesmo modelo de nomenclatura dos blobs do bronze.
    
    Args:
        parquet_docs_weather: Lista de documentos Parquet de meteorologia.
                             Cada documento contém: {"blob_name": str, "parquet_bytes": bytes}
        parquet_docs_water: Lista de documentos Parquet de qualidade da água.
                           Cada documento contém: {"blob_name": str, "parquet_bytes": bytes}
    
    Returns:
        tuple: ((weather_inserted, weather_updated, weather_persisted_docs), 
                (water_inserted, water_updated, water_persisted_docs)).
    """
    blob_service_weather = BlobStorageService(SERVICES["weather"]["blob_container"] + "-silver")
    blob_service_water = BlobStorageService(SERVICES["water"]["blob_container"] + "-silver")
    weather_inserted = 0
    weather_updated = 0
    water_inserted = 0
    water_updated = 0
    weather_persisted_docs = []
    water_persisted_docs = []

    for parquet_doc in parquet_docs_weather:        
        blob_name = parquet_doc["blob_name"].replace(".json", ".parquet")
        
        try:
            # Verifica se o blob já existe
            if blob_service_weather.blob_exists(blob_name): 
                weather_updated += 1
            else:
                weather_inserted += 1
            
            # Armazena o arquivo Parquet no blob storage silver
            blob_client = blob_service_weather._container_client.get_blob_client(blob_name)
            blob_client.upload_blob(parquet_doc["parquet_bytes"], overwrite=True)
            weather_persisted_docs.append(parquet_doc)
        except Exception as e:
            # TODO: Gerar log de falha na persistência de meteorologia
            tratar_erro(
                e,
                f"Falha ao persistir documento Parquet de meteorologia: {blob_name}",
                encerrar=False,
            )

    for parquet_doc in parquet_docs_water:        
        blob_name = parquet_doc["blob_name"].replace(".json", ".parquet")
        
        try:
            # Verifica se o blob já existe
            if blob_service_water.blob_exists(blob_name): 
                water_updated += 1
            else:
                water_inserted += 1
            
            # Armazena o arquivo Parquet no blob storage silver
            blob_client = blob_service_water._container_client.get_blob_client(blob_name)
            blob_client.upload_blob(parquet_doc["parquet_bytes"], overwrite=True)
            water_persisted_docs.append(parquet_doc)
        except Exception as e:
            # TODO: Gerar log de falha na persistência de água
            tratar_erro(
                e,
                f"Falha ao persistir documento Parquet de qualidade da água: {blob_name}",
                encerrar=False,
            )
    
    return (weather_inserted, weather_updated, weather_persisted_docs), (water_inserted, water_updated, water_persisted_docs)


def persist_readings(
    repository: ReadingRepository,
    weather_readings: list,
    water_readings: list,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Persiste leituras no banco de dados.
    
    Args:
        repository: Repositório de leitura.
        weather_readings: Leituras meteorológicas.
        water_readings: Leituras de qualidade da água.
    
    Returns:
        tuple: ((weather_inseridas, weather_atualizadas), (water_inseridas, water_atualizadas)).
    """
    weather_counts = [0, 0]
    water_counts = [0, 0]

    for reading in weather_readings:
        _, updated = repository.save_with_status(reading, SERVICES["weather"]["category_code"])
        weather_counts[updated] += 1

    for reading in water_readings:
        _, updated = repository.save_with_status(reading, SERVICES["water"]["category_code"])
        water_counts[updated] += 1

    return tuple(weather_counts), tuple(water_counts)


def load_saved_readings(
    repository: ReadingRepository,
    selected_station,
    start_date: datetime,
    end_date: datetime,
) -> tuple[list, list]:
    """Carrega leituras persistidas do banco de dados.
    
    Args:
        repository: Repositório de leitura.
        selected_station: Estação selecionada.
        start_date: Data inicial (datetime com UTC).
        end_date: Data final (datetime com UTC).
    
    Returns:
        tuple: (weather_readings, water_readings)
    """
    weather_readings = repository.get_by_station(
        selected_station.id,
        start_date,
        end_date,
        parameter_category_id=1,
    )
    
    water_readings = repository.get_by_station(
        selected_station.id,
        start_date,
        end_date,
        parameter_category_id=2,
    )
    
    return weather_readings, water_readings


def calculate_statistics(
    analytics_service: AnalyticsService,
    weather_readings: list,
    water_readings: list,
) -> tuple[list, list]:
    """Calcula estatísticas para as leituras.
    
    Args:
        analytics_service: Serviço de análise.
        weather_readings: Leituras meteorológicas.
        water_readings: Leituras de qualidade da água.
    
    Returns:
        tuple: (weather_statistics, water_statistics)
    """
    weather_statistics = analytics_service.calculate(weather_readings)
    water_statistics = analytics_service.calculate(water_readings)
    
    return weather_statistics, water_statistics


def run_ingestion_pipeline(
    selected_station,
    start_date_value: date,
    end_date_value: date,
) -> bool:
    """Executa o pipeline de ingestão e persistência (Etapas 1-5.3).
    
    Args:
        selected_station: Estação selecionada.
        start_date_value: Data inicial (date).
        end_date_value: Data final (date).
    
    Returns:
        bool: True se sucesso, False se erro.
    """
    start_time = perf_counter()
    
    progress_bar = st.progress(0, text="Preparando a execução...")
    
    try:
        # Etapa 1: Validar dados
        progress_bar.progress(5, text="Validando os dados informados.")
        
        # Etapa 2: Conectar ao banco
        progress_bar.progress(10, text="Conectando ao banco de dados.")
        repository = ReadingRepository()
        
        # Etapa 3: Preparar ingestão
        progress_bar.progress(15, text="Preparando a ingestão.")
        api_client = APIClient()
        ingestion_datetime = datetime.now(timezone.utc).isoformat()  
        dataParser = DataParser()

        # Converter datas para datetime com UTC
        start_date = datetime.combine(
            start_date_value,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        end_date = datetime.combine(
            end_date_value,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        
        station_metadata = {
            "code": selected_station.code,
            "name": selected_station.name,
            "latitude": float(selected_station.latitude),
            "longitude": float(selected_station.longitude),
        }

        # Etapa 4: Ingestão paralela
        progress_bar.progress(
            20,
            text="Iniciando as consultas meteorológica e hídrica.",
        )
        
        weather_status = st.empty()
        water_status = st.empty()
        
        weather_readings_json_list, water_readings_json_list = run_ingestion(
            api_client,
            selected_station,
            start_date,
            end_date,
            weather_status,
            water_status,
        )
        
        progress_bar.progress(50, text="Consultas às APIs concluídas.")
       
        st.write("Fazendo o parser dos dados....")
        
        # Etapa 5.1: Parser   
        progress_bar.progress(55, text="Fazendo o parser dos dados.")
        readings_weather, documents_weather, readings_water, documents_water = parser_readings(
                    repository,
                    dataParser,
                    ingestion_datetime,
                    station_metadata,
                    selected_station,
                    weather_readings_json_list,
                    water_readings_json_list,
                )
        progress_bar.progress(58, text="Parser dos dados concluído.")

        # Etapa 5.2: Persistência bronze (armazenamento em blob)
        progress_bar.progress(59, text="Persistindo dados bronze.")
        (weather_inserted, weather_updated, weather_persisted_docs), (water_inserted, water_updated, water_persisted_docs) = persist_readings_bronze(
            documents_weather,
            documents_water,
        )
        progress_bar.progress(60, text="Persistência bronze concluída.") 
        st.write(f"Meteorologia: {weather_inserted} documento(s) inserido(s) e {weather_updated} atualizado(s) no bronze.")
        st.write(f"Qualidade da água: {water_inserted} documento(s) inserido(s) e {water_updated} atualizado(s) no bronze.")

        # Etapa 5.2.1: Conversão para Parquet
        progress_bar.progress(62, text="Convertendo documentos bronze para Parquet.")
        weather_parquet_docs = []
        for doc in weather_persisted_docs:
            try:
                parquet_bytes = json_to_parquet(doc["document"])
                weather_parquet_docs.append({
                    "blob_name": doc["blob_name"],
                    "parquet_bytes": parquet_bytes
                })
            except Exception as e:
                tratar_erro(
                    e,
                    f"Falha ao converter documento de meteorologia para Parquet: {doc['blob_name']}",
                    encerrar=False,
                )
        
        water_parquet_docs = []
        for doc in water_persisted_docs:
            try:
                parquet_bytes = json_to_parquet(doc["document"])
                water_parquet_docs.append({
                    "blob_name": doc["blob_name"],
                    "parquet_bytes": parquet_bytes
                })
            except Exception as e:
                tratar_erro(
                    e,
                    f"Falha ao converter documento de água para Parquet: {doc['blob_name']}",
                    encerrar=False,
                )
        
        progress_bar.progress(64, text="Conversão para Parquet concluída.")
        st.write(f"Meteorologia: {len(weather_parquet_docs)} documento(s) convertido(s) para Parquet.")
        st.write(f"Qualidade da água: {len(water_parquet_docs)} documento(s) convertido(s) para Parquet.")

        # Etapa 5.2.2: Persistência silver (armazenamento em Parquet)
        progress_bar.progress(66, text="Persistindo dados Parquet no silver.")
        (weather_inserted_silver, weather_updated_silver, weather_silver_persisted_docs), (water_inserted_silver, water_updated_silver, water_silver_persisted_docs) = persist_readings_silver(
            weather_parquet_docs,
            water_parquet_docs,
        )
        progress_bar.progress(70, text="Persistência silver (Parquet) concluída.")
        st.write(f"Meteorologia: {weather_inserted_silver} arquivo(s) Parquet inserido(s) e {weather_updated_silver} atualizado(s) no silver.")
        st.write(f"Qualidade da água: {water_inserted_silver} arquivo(s) Parquet inserido(s) e {water_updated_silver} atualizado(s) no silver.")

        # Etapa 5.3: Persistência silver (banco de dados)
        progress_bar.progress(72, text="Persistindo leituras no banco de dados (silver).")
        
        (weather_inserted, weather_updated), (water_inserted, water_updated) = persist_readings(
            repository,
            readings_weather,
            readings_water,
        )
        progress_bar.progress(85, text="Persistência em banco de dados concluída.")
        st.write(f"Meteorologia: {weather_inserted} leitura(s) inserida(s) e {weather_updated} atualizada(s).")
        st.write(f"Qualidade da água: {water_inserted} leitura(s) inserida(s) e {water_updated} atualizada(s).")        
        
        # Conclusão
        progress_bar.progress(100, text="Pipeline de ingestão concluído com sucesso.")
        
        elapsed_time = perf_counter() - start_time        
        st.success("Pipeline de ingestão concluído com sucesso!")
        return True
    
    except Exception as e:
        tratar_erro(
            e,
            "Falha durante o pipeline de ingestão no Streamlit",
            encerrar=False,
        )  
        
        st.error(
            "Não foi possível concluir o pipeline de ingestão. Consulte os logs para obter mais detalhes."
        )
        
        return False


def run_analytics_pipeline(
    selected_station,
    start_date_value: date,
    end_date_value: date,
) -> bool:
    """Executa o pipeline de analytics e relatórios (Etapas 6-8).
    
    Args:
        selected_station: Estação selecionada.
        start_date_value: Data inicial (date).
        end_date_value: Data final (date).
    
    Returns:
        bool: True se sucesso, False se erro.
    """
    start_time = perf_counter()
    
    progress_bar = st.progress(0, text="Preparando a execução...")
    
    try:
        # Conectar ao banco
        progress_bar.progress(10, text="Conectando ao banco de dados.")
        repository = ReadingRepository()
        
        # Converter datas para datetime com UTC
        start_date = datetime.combine(
            start_date_value,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        end_date = datetime.combine(
            end_date_value,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        
        # Etapa 6: Recuperar dados
        progress_bar.progress(30, text="Recuperando dados persistidos.")
        
        weather_from_db, water_from_db = load_saved_readings(
            repository,
            selected_station,
            start_date,
            end_date,
        )
        
        st.write(f"Meteorologia: {len(weather_from_db)} leitura(s) recuperada(s).")
        st.write(f"Qualidade da água: {len(water_from_db)} leitura(s) recuperada(s).")
        
        # Etapa 7: Analytics
        progress_bar.progress(60, text="Calculando estatísticas.")
        
        st.write("Calculando as estatísticas...")
        
        analytics_service = AnalyticsService(repository)
        weather_statistics, water_statistics = calculate_statistics(
            analytics_service,
            weather_from_db,
            water_from_db,
        )
        
        # Etapa 8: Exportar CSV
        progress_bar.progress(85, text="Gerando arquivos CSV.")
        
        st.write("Exportando estatísticas para CSV...")
        
        weather_csv = None
        weather_outliers = None
        water_csv = None
        water_outliers = None
        
        if weather_statistics:
            weather_csv = export_statistics_to_csv(
                weather_statistics,
                "weather",
            )
            weather_outliers = export_statistics_with_outliers_detail(
                weather_statistics,
                "weather",
            )
        
        if water_statistics:
            water_csv = export_statistics_to_csv(
                water_statistics,
                "water",
            )
            water_outliers = export_statistics_with_outliers_detail(
                water_statistics,
                "water",
            )
        
        # Salvar no session state
        st.session_state.weather_statistics = weather_statistics
        st.session_state.water_statistics = water_statistics
        st.session_state.weather_csv_path = weather_csv
        st.session_state.weather_outliers_path = weather_outliers
        st.session_state.water_csv_path = water_csv
        st.session_state.water_outliers_path = water_outliers
        st.session_state.selected_station_name = selected_station.name
        st.session_state.selected_period = (
            f"{start_date_value} até {end_date_value}"
        )
        
        # Conclusão
        progress_bar.progress(100, text="Pipeline de analytics concluído com sucesso.")
        
        elapsed_time = perf_counter() - start_time        
        st.success("Pipeline de analytics concluído com sucesso!")
        return True
    
    except Exception as e:
        tratar_erro(
            e,
            "Falha durante o pipeline de analytics no Streamlit",
            encerrar=False,
        )  
        
        st.error(
            "Não foi possível concluir o pipeline de analytics. Consulte os logs para obter mais detalhes."
        )
        
        return False


def run_pipeline(
    selected_station,
    start_date_value: date,
    end_date_value: date,
) -> bool:
    """Executa o pipeline completo de análise (mantido por compatibilidade).
    
    Args:
        selected_station: Estação selecionada.
        start_date_value: Data inicial (date).
        end_date_value: Data final (date).
    
    Returns:
        bool: True se sucesso, False se erro.
    """
    success_ingestion = run_ingestion_pipeline(selected_station, start_date_value, end_date_value)
    
    if success_ingestion:
        success_analytics = run_analytics_pipeline(selected_station, start_date_value, end_date_value)
        return success_analytics
    
    return False
