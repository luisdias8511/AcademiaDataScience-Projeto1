"""ETL para qualidade da água - consulta API real da Meersens."""

import hashlib
import json
import os
from datetime import datetime

import pandas as pd
# Importa a biblioteca responsável por realizar requisições HTTP.
import requests  # type: ignore[import-unresolved]

from dotenv import load_dotenv

from src.database.reading_repository import ReadingRepository
from src.security import security
from src.security.log_utils import tratar_erro
from src.config import logger

# Carrega variáveis de ambiente
load_dotenv()

# Carrega URL da API do .env
API_URL_WATER = os.getenv(
    "API_URL_WATER"
)

# Cache de parâmetros para evitar múltiplas consultas ao BD
_water_params_cache = None


def get_water_parameters_cached() -> list[str]:
    """Retorna parâmetros do cache (sem consultar BD múltiplas vezes)."""
    global _water_params_cache
    if _water_params_cache is None:
        repository = ReadingRepository()
        _water_params_cache = repository.get_water_parameters_codes()
    return _water_params_cache


# Define a função que recupera a chave da API já processada pelo módulo de segurança.
def get_api_key() -> str:
    if not hasattr(security, "api_key_real") or not security.api_key_real:
        raise ValueError(
            "A chave da API não foi carregada pelo módulo src.security.security. "
            "Verifique o conteúdo do arquivo .env e a variavel API_KEY_CRIPTOGRAFADA."
        )

    return security.api_key_real


def _fetch_water_history(
    lat: float,
    lng: float,
    from_date: str,
    to_date: str,
    page: int = 0,
) -> dict:
    """Realiza a requisição HTTP para a API de histórico de qualidade da água."""
    response = requests.get(
        API_URL_WATER,
        headers={"apikey": get_api_key()},
        params={
            "lat": lat,
            "lng": lng,
            "from": from_date,
            "to": to_date,
            "page": page,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _normalize_water_data(payload: dict) -> pd.DataFrame:
    """Converte o payload da API em um DataFrame com colunas aninhadas achatadas."""
    values = payload.get("values")
    if values is None:
        raise KeyError("A resposta da API não contém a chave 'values'.")
    if not isinstance(values, list):
        raise TypeError("A chave 'values' da API deve ser uma lista.")

    df = pd.json_normalize(values, sep="_")

    if "found" in payload:
        df["response_found"] = payload["found"]

    return df


def _extract_parameter_columns(
    df: pd.DataFrame,
    parameter_codes: list[str],
) -> pd.DataFrame:
    """Seleciona os valores da API cujos códigos existem no banco."""
    if df.empty:
        columns = ["datetime"] + [
            f"pollutants_{code}_value" for code in parameter_codes
        ]
        return pd.DataFrame(columns=columns)

    parameter_columns = [
        f"pollutants_{code}_value"
        for code in parameter_codes
        if f"pollutants_{code}_value" in df.columns
    ]

    if not parameter_columns:
        raise KeyError(
            "Nenhum código de parâmetro do banco corresponde aos parâmetros "
            "retornados pela API de água."
        )

    columns = (["datetime"] if "datetime" in df.columns else []) + parameter_columns
    return df[columns]


def consulta_api(
    lat: float,
    lng: float,
    from_date: datetime,
    to_date: datetime,
) -> pd.DataFrame:
    """Percorre todas as páginas e retorna os parâmetros de água cadastrados no banco.
    
    Args:
        lat: Latitude da localização
        lng: Longitude da localização
        from_date: Data inicial (datetime object)
        to_date: Data final (datetime object)
        
    Returns:
        DataFrame com colunas "datetime" e "pollutants_*_value" para cada parâmetro
    """
    logger.info(
        "Iniciando consulta de qualidade da água para latitude=%s, longitude=%s, período=%s a %s.",
        lat,
        lng,
        from_date,
        to_date,
    )
    try:
        # Converter datetime para string no formato ISO 8601
        from_date_str = from_date.isoformat() if isinstance(from_date, datetime) else str(from_date)
        to_date_str = to_date.isoformat() if isinstance(to_date, datetime) else str(to_date)
        
        repository = ReadingRepository()
        # Usar cache de parâmetros (não consultar BD múltiplas vezes)
        parameter_codes = get_water_parameters_cached()

        pages: list[pd.DataFrame] = []
        seen_pages: set[str] = set()
        page = 0

        while True:
            payload = _fetch_water_history(
                lat,
                lng,
                from_date_str,
                to_date_str,
                page=page,
            )
            page_df = _normalize_water_data(payload)
            if page_df.empty:
                break

            # Hash MD5 (32 bytes) em vez de JSON completo (50KB+)
            page_json = json.dumps(payload["values"], default=str)
            page_signature = hashlib.md5(page_json.encode()).hexdigest()
            
            if page_signature in seen_pages:
                raise RuntimeError(
                    f"A API repetiu os dados da página {page}; "
                    "a varredura foi interrompida para evitar um loop infinito."
                )
            seen_pages.add(page_signature)
            pages.append(page_df)
            page += 1

        df = pd.concat(pages, ignore_index=True) if pages else pd.DataFrame()
        parametros = _extract_parameter_columns(df, parameter_codes)
        logger.info(
            "Consulta de qualidade da água concluída: %d página(s), %d registro(s), %d parâmetro(s).",
            len(pages),
            len(parametros),
            len(parameter_codes),
        )
        print(parametros.head())

        return parametros
    except Exception as e:
        tratar_erro(e, "Falha durante a consulta e ingestão dos dados de qualidade da água", encerrar=True)

