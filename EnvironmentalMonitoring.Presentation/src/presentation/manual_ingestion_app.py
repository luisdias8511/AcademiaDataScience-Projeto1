"""Página de ingestão manual de dados ambientais via upload de JSON."""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import streamlit as st

from src.database.reading_repository import ReadingRepository
from src.database.user_repository import UserRepository
from src.database.blob_storage_service import BlobStorageService
from src.ingestion.data_parser import DataParser
from src.models.operator import Operator
from src.models.station import Station
from src.security.log_utils import tratar_erro
from src.constants import SERVICES
from src.config import logger
from src.presentation.streamlit_support import load_stations


def get_operator_by_username(username: str) -> Operator | None:
    """Obtém operador a partir do username do usuário.
    
    Args:
        username: Nome de usuário.
    
    Returns:
        Operator se encontrado, None caso contrário.
    """
    try:
        user_repo = UserRepository()
        users = user_repo.list_users()
        
        # Procurar usuário pelo username
        user = next((u for u in users if u["username"] == username), None)
        if not user:
            return None
        
        user_id = user["id_usuario"]
        
        # Procurar operador com esse UserId
        reading_repo = ReadingRepository()
        reading_repo._connect()
        try:
            cursor = reading_repo.conn.cursor()
            cursor.execute(
                "SELECT Id, UserId, ServiceId FROM Operators WHERE UserId = ?",
                user_id,
            )
            row = cursor.fetchone()
            reading_repo._disconnect()
            
            if row:
                return Operator(id=row[0], user_id=row[1], service_id=row[2])
            return None
        except Exception:
            reading_repo._disconnect()
            raise
    except Exception as e:
        logger.error(f"Erro ao buscar operador para usuário {username}: {e}")
        return None


def normalize_json_format(json_data: dict) -> str:
    """Detecta o formato do JSON.
    
    Args:
        json_data: Dados JSON a analisar.
    
    Returns:
        "meersens" ou "simplified"
    """
    # Verificar se é formato Meersens
    if "values" in json_data and isinstance(json_data.get("values"), list):
        first_value = json_data["values"][0] if json_data["values"] else {}
        
        # Formato Meersens: parameters é um objeto com estrutura complexa
        if isinstance(first_value.get("parameters"), dict):
            first_param = next(iter(first_value.get("parameters", {}).values()), {})
            if isinstance(first_param, dict) and "value" in first_param:
                return "meersens"
    
    # Se chegou aqui, assume formato simplificado
    return "simplified"


def normalize_meersens_values(json_data: dict, domain: str, station_code: str) -> dict:
    """Converte valores Meersens para formato simplificado.
    
    Args:
        json_data: JSON original do Meersens.
        domain: Domínio ("weather" ou "water").
        station_code: Código da estação.
    
    Returns:
        JSON normalizado.
    """
    # Determinar specifications_name com base no domínio
    if domain == "weather":
        specifications_name = SERVICES["weather"]["specifications_name"]  # "parameters"
    else:
        specifications_name = SERVICES["water"]["specifications_name"]   # "pollutants"
    
    # Normalizar valores
    normalized_values = []
    
    for reading in json_data.get("values", []):
        if not reading.get("found", True):
            continue
        
        datetime_str = reading.get("datetime")
        parameters = reading.get("parameters", {})
        
        if not datetime_str or not parameters:
            continue
        
        # Extrair valores dos parâmetros Meersens
        # Formato Meersens: {"parameter_name": {"value": 12.55, "unit": "°C", ...}}
        # Preservar estrutura completa: {"value": ..., "unit": ..., "name": ...}
        normalized_params = {}
        for param_name, param_data in parameters.items():
            if isinstance(param_data, dict) and "value" in param_data:
                normalized_params[param_name] = {
                    "value": param_data["value"],
                    "unit": param_data.get("unit", ""),
                    "name": param_data.get("name", param_name),
                }
        
        if normalized_params:
            normalized_values.append({
                "datetime": datetime_str,
                specifications_name: normalized_params,
            })
    
    if not normalized_values:
        raise ValueError("Nenhum valor válido encontrado no JSON")
    
    # Criar JSON normalizado
    normalized_json = {
        "metadata": {
            "domain": domain,
            "station": {"code": station_code},
            "source": "meersens",
        },
        "values": normalized_values,
    }
    
    return normalized_json


def show_manual_ingestion_page():
    """Página principal de ingestão manual de dados ambientais."""
    
    st.markdown("Carregue um arquivo JSON com dados ambientais para persistência manual.")
    st.divider()
    
    # Seção 1: Validação de Usuário
    st.subheader("1️⃣ Validação de Usuário")
    username = st.text_input(
        "Username",
        placeholder="Teste10",
        key="manual_ingestion_username",
    )
    
    operator = None
    if username:
        operator = get_operator_by_username(username)
        if operator:
            st.success(f"✅ Usuário encontrado (Operador ID: {operator.id})")
        else:
            st.error("❌ Usuário não encontrado ou sem operador associado.")
    
    st.divider()
    
    # Seção 2: Upload do JSON
    st.subheader("2️⃣ Upload do Arquivo JSON")
    uploaded_file = st.file_uploader(
        "Selecione um arquivo JSON",
        type=["json"],
        key="manual_ingestion_upload",
    )
    
    if not uploaded_file or not operator:
        st.info("Preencha o username e valide o operador antes de fazer upload.")
        return
    
    # Seção 3: Processamento
    st.divider()
    st.subheader("3️⃣ Processamento")
    
    try:
        # Ler e parsear JSON
        file_content = uploaded_file.read().decode("utf-8")
        json_data = json.loads(file_content)
        
        st.info(f"✅ Arquivo JSON lido com sucesso ({len(file_content)} bytes)")
        
        # Detectar formato
        json_format = normalize_json_format(json_data)
        
        # Se é Meersens, solicitar domínio e código da estação
        if json_format == "meersens":
            st.info("📋 Formato Meersens detectado. Forneça informações adicionais.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                domain = st.radio(
                    "Selecione o domínio:",
                    ["weather", "water"],
                    format_func=lambda x: "🌤️ Meteorologia" if x == "weather" else "💧 Qualidade da Água",
                    key="meersens_domain_select",
                )
            
            with col2:
                # Carregar estações disponíveis
                stations = load_stations()
                if not stations:
                    st.error("❌ Nenhuma estação disponível no banco de dados.")
                    return
                
                # Criar dicionário de opções de estações
                station_options = {
                    f"{station.name}": station
                    for station in stations
                }
                
                # Selectbox para escolher estação
                selected_station_label = st.selectbox(
                    "Selecione a estação:",
                    options=list(station_options.keys()),
                    key="meersens_station_select",
                )
                
                selected_station = station_options[selected_station_label]
                station_code = selected_station.code
            
            if not station_code or not domain:
                st.warning("⚠️ Preencha domínio e estação para continuar.")
                return
            
            # Normalizar JSON Meersens
            try:
                normalized_json = normalize_meersens_values(json_data, domain, station_code)
            except ValueError as e:
                st.error(f"❌ Erro ao normalizar JSON: {e}")
                return
        else:
            # Formato simplificado
            normalized_json = json_data
            
            # Validar estrutura
            if "metadata" not in normalized_json:
                st.error("❌ JSON inválido: falta campo 'metadata'")
                return
            
            metadata = normalized_json["metadata"]
            domain = metadata.get("domain")
            
            if not domain:
                st.error("❌ JSON inválido: falta campo 'metadata.domain'")
                return
        
        if domain not in ["weather", "water"]:
            st.error(f"❌ Domínio inválido: '{domain}'. Use 'weather' ou 'water'.")
            return
        
        st.success(f"✅ JSON processado como domínio: {domain}")
        
        # Determinar categoria
        if domain == "weather":
            category_code = SERVICES["weather"]["category_code"]
            category_name = "Meteorologia"
        else:
            category_code = SERVICES["water"]["category_code"]
            category_name = "Qualidade da Água"
        
        st.info(f"📊 Categoria: {category_name}")
        
        # Botão de execução
        if st.button("Executar Ingestão", type="primary", use_container_width=True):
            execute_manual_ingestion(
                normalized_json,
                domain,
                category_code,
                operator,
                username,
            )
    
    except json.JSONDecodeError as e:
        st.error(f"❌ Erro ao parsear JSON: {e}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")


def execute_manual_ingestion(
    json_data: dict,
    domain: str,
    category_code: str,
    operator: Operator,
    username: str,
):
    """Executa a ingestão manual dos dados.
    
    Args:
        json_data: Dados do JSON enviado.
        domain: Domínio (weather ou water).
        category_code: Código da categoria.
        operator: Operador que executa a ingestão.
        username: Username do operador.
    """
    try:
        progress_bar = st.progress(0, text="Iniciando ingestão manual...")
        
        # Etapa 1: Preparar
        progress_bar.progress(10, text="Preparando dados...")
        
        repository = ReadingRepository()
        dataParser = DataParser()
        ingestion_datetime = datetime.now(timezone.utc).isoformat()
        
        # Obter estação do JSON
        json_metadata = json_data.get("metadata", {})
        station_metadata = json_metadata.get("station", {})
        station_code = station_metadata.get("code")
        
        if not station_code:
            st.error("❌ JSON inválido: falta campo 'metadata.station.code'")
            return
        
        # Buscar estação no banco
        # Procurar por code
        repository._connect()
        try:
            cursor = repository.conn.cursor()
            cursor.execute(
                "SELECT Id, Code, Name, Latitude, Longitude, Municipality, State, Country FROM Stations WHERE Code = ?",
                station_code,
            )
            row = cursor.fetchone()
            repository._disconnect()
            
            if not row:
                st.error(f"❌ Estação não encontrada: {station_code}")
                return
            
            station = Station(
                id=row[0],
                code=row[1],
                name=row[2],
                latitude=Decimal(str(row[3])),
                longitude=Decimal(str(row[4])),
                municipality=row[5],
                state=row[6],
                country=row[7],
            )
        except Exception as e:
            repository._disconnect()
            raise
        
        st.success(f"✅ Estação encontrada: {station.name}")
        progress_bar.progress(20, text="Validando parâmetros...")
        
        # Etapa 2: Validar parâmetros
        allowed_parameters = repository.get_parameters_by_CategoryCode(category_code)
        
        if not allowed_parameters:
            st.error(f"❌ Nenhum parâmetro encontrado para categoria: {category_code}")
            return
        
        st.success(f"✅ {len(allowed_parameters)} parâmetro(s) encontrado(s)")
        progress_bar.progress(30, text="Parseando dados...")
        
        # Etapa 3: Parsear dados
        ingestion_metadata = {
            "contract_version": "1.0",
            "source": {"type": "manual", "operator": username},
            "ingestion_datetime": ingestion_datetime,
            "station": {
                "code": station.code,
                "name": station.name,
                "latitude": float(station.latitude),
                "longitude": float(station.longitude),
            },
        }
        
        # Determinar specifications_name
        if domain == "weather":
            specifications_name = SERVICES["weather"]["specifications_name"]
        else:
            specifications_name = SERVICES["water"]["specifications_name"]
        
        # Parser
        readings, documents = dataParser.build_documents_readings(
            specifications_name=specifications_name,
            original_page_json=json_data,
            metadata=ingestion_metadata,
            station_id=station.id,
            operator=operator,
            allowed_parameters=allowed_parameters,
            category_code=category_code,
        )
        
        if not readings:
            st.warning("⚠️ Nenhuma leitura válida foi extraída do JSON")
            return
        
        st.success(f"✅ {len(readings)} leitura(s) parseada(s)")
        progress_bar.progress(50, text="Persistindo no blob storage...")
        
        # Etapa 4: Persistir no blob storage
        blob_service = BlobStorageService(
            SERVICES[domain]["blob_container"]
        )
        
        inserted_count = 0
        updated_count = 0
        
        for document in documents:
            if blob_service.blob_exists(document["blob_name"]):
                updated_count += 1
            else:
                inserted_count += 1
            blob_service.upload_json(document["blob_name"], document["document"])
        
        st.success(f"✅ Blob storage: {inserted_count} inserido(s), {updated_count} atualizado(s)")
        progress_bar.progress(75, text="Persistindo no banco de dados...")
        
        # Etapa 5: Persistir no banco de dados
        db_inserted = 0
        db_updated = 0
        
        for reading in readings:
            reading_id, is_updated = repository.save_with_status(reading, category_code)
            if is_updated:
                db_updated += 1
            else:
                db_inserted += 1
        
        st.success(f"✅ Banco de dados: {db_inserted} inserido(s), {db_updated} atualizado(s)")
        progress_bar.progress(100, text="Ingestão concluída com sucesso!")
        
        # Resumo final
        st.divider()
        st.subheader("✅ Ingestão Concluída")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Leituras Processadas", len(readings))
            st.metric("Blob Storage - Inseridos", inserted_count)
        with col2:
            st.metric("Documentos Armazenados", len(documents))
            st.metric("Banco de Dados - Atualizados", db_updated)
        
        logger.info(
            f"Ingestão manual concluída: {len(readings)} leituras, "
            f"operador={username}, domínio={domain}"
        )
    
    except Exception as e:
        st.error(f"❌ Erro durante ingestão: {str(e)}")
        logger.error(f"Erro na ingestão manual: {e}")
        tratar_erro(e, "Falha durante ingestão manual", encerrar=False)
