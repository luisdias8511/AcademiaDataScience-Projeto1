
"""Cliente para consumir a APIs de dados meteorológicos e de qualidade da água."""

import os
from datetime import datetime
from decimal import Decimal

import requests  # type: ignore[import-unresolved]

from dotenv import load_dotenv

from src.security import security
from src.config import logger
from src.models import Station

# Carrega variáveis de ambiente
load_dotenv()


def get_api_key() -> str:
    """Recupera a chave da API já processada pelo módulo de segurança.
    
    Returns:
        Chave da API descriptografada.
    
    Raises:
        ValueError: Se a chave não foi carregada pelo módulo de segurança.
    """
    if not hasattr(security, "api_key_real") or not security.api_key_real:
        raise ValueError(
            "A chave da API não foi carregada pelo módulo src.security.security. "
            "Verifique o conteúdo do arquivo .env e a variável API_KEY_CRIPTOGRAFADA."
        )

    return security.api_key_real


class APIClient:
    """Cliente para consumir dados meteorológicos e de qualidade da água.
    
    Responsabilidades:
    - Realizar requisições HTTP à API
    - Tratar autenticação e headers
    - Validar respostas
    - Retornar JSON bruto sem transformação
    """

    TIMEOUT = 30

    def __init__(self) -> None:
        """Inicializa o cliente com a chave da API."""
        self.api_key = get_api_key()

    def fetch(
        self,
        latitude: Decimal,
        longitude: Decimal,
        start_date: datetime,
        end_date: datetime,
        api_url_env: str,
        page: int = 0,
    ) -> dict:
        """Realiza requisição à API de histórico.
        
        Args:
            latitude: Latitude da estação.
            longitude: Longitude da estação.
            start_date: Data/hora inicial do período (formato ISO).
            end_date: Data/hora final do período (formato ISO).
            page: Número da página para paginação (padrão: 0).
        
        Returns:
            Dicionário com a resposta JSON da API.
        
        Raises:
            requests.RequestException: Se a requisição falhar.
            ValueError: Se os parâmetros forem inválidos.
        """
        # Validar parâmetros
        if latitude is None or longitude is None:
            raise ValueError("Latitude e longitude são obrigatórias.")

        if not start_date or not end_date:
            raise ValueError("Datas inicial e final são obrigatórias.")

        # Converter para strings ISO se necessário
        start_str = (
            start_date.isoformat()
            if isinstance(start_date, datetime)
            else str(start_date)
        )
        end_str = (
            end_date.isoformat()
            if isinstance(end_date, datetime)
            else str(end_date)
        )
        # preparar url
        API_URL = os.getenv(
            api_url_env
        )
        # Preparar headers
        headers = {"apikey": self.api_key}

        # Preparar parâmetros
        params = {
            "lat": float(latitude),
            "lng": float(longitude),
            "from": start_str,
            "to": end_str,
            "page": page,
        }

        logger.debug(
            "Requisição à API: latitude=%s, longitude=%s, período=%s a %s, página=%d",
            latitude,
            longitude,
            start_str,
            end_str,
            page,
        )

        # Realizar requisição
        try:
            response = requests.get(
                API_URL,
                headers=headers,
                params=params,
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()

            logger.debug(
                "Requisição à API bem-sucedida: status=%d",
                response.status_code,
            )

            return response.json()

        except requests.exceptions.Timeout:
            logger.error("Timeout ao conectar à API.")
            raise
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com a API.")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error("Erro HTTP da API: %s", e)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Erro ao fazer requisição à API: %s", e)
            raise
    
    def fetch_readings(
        self,
        station: Station,
        start_date: datetime,
        end_date: datetime,
        api_url_env: str
    ) -> list[dict]:
        """Realiza requisição à API de histórico.
        
        Args:
            station: Estação de onde se deseja obter os dados.
            start_date: Data/hora inicial do período (formato ISO).
            end_date: Data/hora final do período (formato ISO).
            page: Número da página para paginação (padrão: 0).
        
        Returns:
            Dicionário com a resposta JSON da API.
        
        Raises:
            requests.RequestException: Se a requisição falhar.
            ValueError: Se os parâmetros forem inválidos.
        """
        # Validar parâmetros
        if not station:
            raise ValueError("Estação é obrigatória.")

        if not start_date or not end_date:
            raise ValueError("Datas inicial e final são obrigatórias.")

        # Converter para strings ISO se necessário
        start_str = (
            start_date.isoformat()
            if isinstance(start_date, datetime)
            else str(start_date)
        )
        end_str = (
            end_date.isoformat()
            if isinstance(end_date, datetime)
            else str(end_date)
        )

        pages: list[dict] = []

        page = 0

        while True:
            payload = self.fetch(
                
                station.latitude,
                station.longitude,
                start_str,
                end_str,
                page=page,
                api_url_env=api_url_env,
            )
            if payload:
                pages.append(payload)

            if (payload and payload.get("page") and payload["page"].get("totalPages") and 
                payload["page"]["totalPages"] > 0 and 
                payload["page"].get("pageNumber") < payload["page"]["totalPages"] - 1):
                page += 1
            else:
                break

        return pages
