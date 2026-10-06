"""Funções de suporte para a interface Streamlit.

Este módulo contém todas as funções auxiliares para a aplicação de
Monitoramento Ambiental, incluindo carregamento de dados, validação,
processamento de pipeline e renderização de componentes.
"""

from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st

from src.database.reading_repository import ReadingRepository
from src.services.api_weather_service import IngestionService
from src.analytics.service import AnalyticsService
from src.models.statistics_result import StatisticsResult
from src.reporting import (
    export_statistics_to_csv,
    export_statistics_with_outliers_detail,
)
from src.security.log_utils import tratar_erro


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
    ingestion_service: IngestionService,
    selected_station,
    start_date: datetime,
    end_date: datetime,
    weather_status,
    water_status,
) -> tuple[list, list]:
    """Executa ingestion de weather e water em paralelo.
    
    Args:
        ingestion_service: Serviço de ingestão.
        selected_station: Estação selecionada.
        start_date: Data inicial (datetime com UTC).
        end_date: Data final (datetime com UTC).
        weather_status: Placeholder para status de weather.
        water_status: Placeholder para status de water.
    
    Returns:
        tuple: (weather_readings, water_readings)
    """
    weather_readings = []
    water_readings = []
    
    weather_status.info("Meteorologia: consulta em andamento...")
    water_status.info("Qualidade da água: consulta em andamento...")
    
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    ingestion_service.fetch_weather_readings,
                    selected_station,
                    start_date,
                    end_date,
                ): "weather",
                executor.submit(
                    ingestion_service.get_water_readings,
                    selected_station,
                    start_date,
                    end_date,
                ): "water",
            }
            
            for future in as_completed(futures):
                category = futures[future]
                readings = future.result()
                
                if category == "weather":
                    weather_readings = readings
                    weather_status.success(
                        f"Meteorologia: {len(weather_readings)} leitura(s) coletada(s)."
                    )
                elif category == "water":
                    water_readings = readings
                    water_status.success(
                        f"Qualidade da água: {len(water_readings)} leitura(s) coletada(s)."
                    )
    
    except Exception as e:
        weather_status.error("Falha na consulta meteorológica.")
        water_status.error("Falha na consulta de qualidade da água.")
        raise
    
    return weather_readings, water_readings


def persist_readings(
    repository: ReadingRepository,
    weather_readings: list,
    water_readings: list,
) -> tuple[int, int]:
    """Persiste leituras no banco de dados.
    
    Args:
        repository: Repositório de leitura.
        weather_readings: Leituras meteorológicas.
        water_readings: Leituras de qualidade da água.
    
    Returns:
        tuple: (weather_count, water_count) de registros persistidos.
    """
    weather_count = 0
    water_count = 0
    
    if weather_readings:
        weather_ids = repository.save_many(
            weather_readings,
            parameter_category_id=1,
        )
        weather_count = len(weather_ids) if weather_ids else 0
        st.write(f"{weather_count} leitura(s) meteorológica(s) persistida(s).")
    
    if water_readings:
        water_ids = repository.save_many(
            water_readings,
            parameter_category_id=2,
        )
        water_count = len(water_ids) if water_ids else 0
        st.write(f"{water_count} leitura(s) de água persistida(s).")
    
    return weather_count, water_count


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


def run_pipeline(
    selected_station,
    start_date_value: date,
    end_date_value: date,
) -> bool:
    """Executa o pipeline completo de análise.
    
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
        ingestion_service = IngestionService()
        
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
        
        # Etapa 4: Ingestão paralela
        progress_bar.progress(
            20,
            text="Iniciando as consultas meteorológica e hídrica.",
        )
        
        weather_status = st.empty()
        water_status = st.empty()
        
        weather_readings, water_readings = run_ingestion(
            ingestion_service,
            selected_station,
            start_date,
            end_date,
            weather_status,
            water_status,
        )
        
        progress_bar.progress(50, text="Consultas às APIs concluídas.")
        
        st.write("Persistindo as leituras no SQL Server...")
        
        # Etapa 5: Persistência
        progress_bar.progress(60, text="Persistindo dados meteorológicos.")
        progress_bar.progress(70, text="Persistindo dados de qualidade da água.")
        
        weather_count, water_count = persist_readings(
            repository,
            weather_readings,
            water_readings,
        )
        
        # Etapa 6: Recuperar dados
        progress_bar.progress(80, text="Recuperando dados persistidos.")
        
        weather_from_db, water_from_db = load_saved_readings(
            repository,
            selected_station,
            start_date,
            end_date,
        )
        
        # Etapa 7: Analytics
        progress_bar.progress(90, text="Calculando estatísticas.")
        
        st.write("Calculando as estatísticas...")
        
        analytics_service = AnalyticsService(repository)
        weather_statistics, water_statistics = calculate_statistics(
            analytics_service,
            weather_from_db,
            water_from_db,
        )
        
        # Etapa 8: Exportar CSV
        progress_bar.progress(95, text="Gerando arquivos CSV.")
        
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
        
        # Etapa 9: Conclusão
        progress_bar.progress(100, text="Fluxo concluído com sucesso.")
        
        elapsed_time = perf_counter() - start_time        
        st.success("Fluxo concluído com sucesso!")
        return True
    
    except Exception as e:
        tratar_erro(
            e,
            "Falha durante a execução da interface Streamlit",
            encerrar=False,
        )  
        
        st.error(
            "Não foi possível concluir o fluxo. Consulte os logs para obter mais detalhes."
        )
        
        return False
