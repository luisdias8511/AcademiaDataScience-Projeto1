"""Testes para o módulo de ingestão de dados (água e clima).

Cobre clientes HTTP, parsers e transformações de dados de APIs externas.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
import json

from src.ingestion.water_client import MeersensWaterClient, get_api_key
from src.ingestion.weather_client import MeersensWeatherClient
from src.ingestion.water_parser import WaterParser
from src.ingestion.weather_parser import WeatherParser
from src.database.reading_repository import ReadingRepository
from src.models.reading import Reading
from src.models.reading_value import ReadingValue


class TestWaterClientInitialization:
    """Testes para inicialização e validação do cliente de água."""

    def test_get_api_key_from_security_module(self):
        """Deve recuperar chave da API do módulo de segurança."""
        with patch('src.ingestion.water_client.security') as mock_security:
            mock_security.api_key_real = "test_api_key_12345"
            
            key = get_api_key()
            
            assert key == "test_api_key_12345"

    def test_get_api_key_raises_when_not_loaded(self):
        """Deve lançar ValueError se chave da API não foi carregada."""
        with patch('src.ingestion.water_client.security') as mock_security:
            mock_security.api_key_real = None
            
            with pytest.raises(ValueError) as exc_info:
                get_api_key()
            assert "api" in str(exc_info.value).lower()

    def test_water_client_init_success(self):
        """Deve inicializar cliente de água com chave da API."""
        with patch('src.ingestion.water_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_api_key"
            
            client = MeersensWaterClient()
            
            assert client.api_key == "test_api_key"

    def test_water_client_has_timeout(self):
        """Cliente deve ter timeout configurado."""
        with patch('src.ingestion.water_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_api_key"
            
            client = MeersensWaterClient()
            
            assert client.TIMEOUT == 30


class TestWaterClientFetch:
    """Testes para método fetch do cliente de água."""

    @pytest.fixture
    def water_client(self):
        """Cria cliente de água com mock de chave."""
        with patch('src.ingestion.water_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_key"
            yield MeersensWaterClient()

    def test_fetch_valid_coordinates_and_dates(self, water_client):
        """Deve aceitar coordenadas e datas válidas."""
        with patch('src.ingestion.water_client.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"values": []}
            mock_get.return_value = mock_response
            
            result = water_client.fetch(
                latitude=Decimal("-23.5505"),
                longitude=Decimal("-46.6333"),
                start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
            
            assert result == {"values": []}

    def test_fetch_requires_latitude(self, water_client):
        """Deve lançar ValueError se latitude for None."""
        with pytest.raises(ValueError) as exc_info:
            water_client.fetch(
                latitude=None,
                longitude=Decimal("-46.6333"),
                start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
        assert "latitude" in str(exc_info.value).lower()

    def test_fetch_requires_longitude(self, water_client):
        """Deve lançar ValueError se longitude for None."""
        with pytest.raises(ValueError) as exc_info:
            water_client.fetch(
                latitude=Decimal("-23.5505"),
                longitude=None,
                start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
        assert "longitude" in str(exc_info.value).lower()

    def test_fetch_requires_start_date(self, water_client):
        """Deve lançar ValueError se data inicial for None."""
        with pytest.raises(ValueError) as exc_info:
            water_client.fetch(
                latitude=Decimal("-23.5505"),
                longitude=Decimal("-46.6333"),
                start_date=None,
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
        assert "data" in str(exc_info.value).lower()

    def test_fetch_includes_api_key_in_headers(self, water_client):
        """Deve incluir chave da API nos headers."""
        with patch('src.ingestion.water_client.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"values": []}
            mock_get.return_value = mock_response
            
            water_client.fetch(
                latitude=Decimal("-23.5505"),
                longitude=Decimal("-46.6333"),
                start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
            
            # Verificar que headers incluem apikey
            call_kwargs = mock_get.call_args[1]
            assert "headers" in call_kwargs
            assert "apikey" in call_kwargs["headers"]

    def test_fetch_converts_datetime_to_iso(self, water_client):
        """Deve converter datetime para formato ISO."""
        with patch('src.ingestion.water_client.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"values": []}
            mock_get.return_value = mock_response
            
            start = datetime(2026, 1, 1, 10, 30, 45, tzinfo=timezone.utc)
            end = datetime(2026, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
            
            water_client.fetch(
                latitude=Decimal("-23.5505"),
                longitude=Decimal("-46.6333"),
                start_date=start,
                end_date=end,
            )
            
            # Verificar que as datas foram convertidas para ISO
            call_kwargs = mock_get.call_args[1]
            assert "params" in call_kwargs
            params = call_kwargs["params"]
            assert "from" in params
            assert "to" in params
            # Verificar formato ISO
            assert "T" in params["from"]
            assert "T" in params["to"]

    def test_fetch_with_pagination(self, water_client):
        """Deve suportar paginação."""
        with patch('src.ingestion.water_client.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"values": []}
            mock_get.return_value = mock_response
            
            water_client.fetch(
                latitude=Decimal("-23.5505"),
                longitude=Decimal("-46.6333"),
                start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                page=2,
            )
            
            # Verificar que página foi passada
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["page"] == 2


class TestWeatherClientInitialization:
    """Testes para inicialização do cliente de clima."""

    def test_weather_client_init_success(self):
        """Deve inicializar cliente de clima com chave da API."""
        with patch('src.ingestion.weather_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_api_key"
            
            client = MeersensWeatherClient()
            
            assert client.api_key == "test_api_key"

    def test_weather_client_fetch_valid_params(self):
        """Deve aceitar coordenadas e datas válidas."""
        with patch('src.ingestion.weather_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_key"
            
            with patch('src.ingestion.weather_client.requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {"values": []}
                mock_get.return_value = mock_response
                
                client = MeersensWeatherClient()
                result = client.fetch(
                    latitude=Decimal("-23.5505"),
                    longitude=Decimal("-46.6333"),
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                )
                
                assert result == {"values": []}


class TestWaterParser:
    """Testes para parser de dados de água."""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repositório."""
        return MagicMock(spec=ReadingRepository)

    def test_parser_init_with_repository(self, mock_repository):
        """Deve inicializar com repositório."""
        parser = WaterParser(mock_repository)
        assert parser.repository == mock_repository

    def test_parse_empty_payload(self, mock_repository):
        """Deve lançar ValueError para payload sem 'values'."""
        parser = WaterParser(mock_repository)
        
        with pytest.raises(ValueError):
            parser.parse(
                station_id=1,
                api_payload={},
            )

    def test_parse_valid_water_data(self, mock_repository):
        """Deve converter dados válidos de água em Reading."""
        parser = WaterParser(mock_repository)
        
        payload = {
            "values": [
                {
                    "timestamp": "2026-01-15T10:30:00Z",
                    "ph": 7.5,
                    "condutividade": 450.2,
                }
            ]
        }
        
        # Mock do repositório para retornar parâmetro ID
        mock_repository._get_parameter_id_by_code.return_value = 1
        
        result = parser.parse(
            station_id=1,
            api_payload=payload,
        )
        
        assert isinstance(result, list)

    def test_parse_handles_multiple_timestamps(self, mock_repository):
        """Deve processar múltiplos timestamps."""
        parser = WaterParser(mock_repository)
        
        payload = {
            "values": [
                {
                    "timestamp": "2026-01-15T10:00:00Z",
                    "ph": 7.5,
                },
                {
                    "timestamp": "2026-01-15T11:00:00Z",
                    "ph": 7.6,
                },
            ]
        }
        
        mock_repository._get_parameter_id_by_code.return_value = 1
        
        result = parser.parse(
            station_id=1,
            api_payload=payload,
        )
        
        assert isinstance(result, list)


class TestWeatherParser:
    """Testes para parser de dados de clima."""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repositório."""
        return MagicMock(spec=ReadingRepository)

    def test_parser_init_with_repository(self, mock_repository):
        """Deve inicializar com repositório."""
        parser = WeatherParser(mock_repository)
        assert parser.repository == mock_repository

    def test_parse_empty_payload(self, mock_repository):
        """Deve lançar ValueError para payload sem 'values'."""
        parser = WeatherParser(mock_repository)
        
        with pytest.raises(ValueError):
            parser.parse(
                station_id=1,
                api_payload={},
            )

    def test_parse_valid_weather_data(self, mock_repository):
        """Deve converter dados válidos de clima em Reading."""
        parser = WeatherParser(mock_repository)
        
        payload = {
            "values": [
                {
                    "timestamp": "2026-01-15T10:30:00Z",
                    "temperature": 25.5,
                    "humidity": 65.0,
                }
            ]
        }
        
        mock_repository._get_parameter_id_by_code.return_value = 1
        
        result = parser.parse(
            station_id=1,
            api_payload=payload,
        )
        
        assert isinstance(result, list)


class TestClientErrorHandling:
    """Testes para tratamento de erros em clientes HTTP."""

    def test_water_client_handles_request_error(self):
        """Deve tratar erro de requisição HTTP."""
        with patch('src.ingestion.water_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_key"
            
            with patch('src.ingestion.water_client.requests.get') as mock_get:
                mock_get.side_effect = Exception("Connection error")
                
                client = MeersensWaterClient()
                
                with pytest.raises(Exception) as exc_info:
                    client.fetch(
                        latitude=Decimal("-23.5505"),
                        longitude=Decimal("-46.6333"),
                        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                        end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                    )
                assert "Connection error" in str(exc_info.value)

    def test_weather_client_handles_request_error(self):
        """Deve tratar erro de requisição HTTP."""
        with patch('src.ingestion.weather_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_key"
            
            with patch('src.ingestion.weather_client.requests.get') as mock_get:
                mock_get.side_effect = Exception("Connection error")
                
                client = MeersensWeatherClient()
                
                with pytest.raises(Exception):
                    client.fetch(
                        latitude=Decimal("-23.5505"),
                        longitude=Decimal("-46.6333"),
                        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                        end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                    )


class TestClientIntegration:
    """Testes de integração entre cliente e parser."""

    def test_water_workflow_fetch_and_parse(self):
        """Deve conseguir buscar e fazer parse de dados de água."""
        mock_repo = MagicMock(spec=ReadingRepository)
        mock_repo._get_parameter_id_by_code.return_value = 1
        
        with patch('src.ingestion.water_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_key"
            
            with patch('src.ingestion.water_client.requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "values": [
                        {
                            "timestamp": "2026-01-15T10:30:00Z",
                            "ph": 7.5,
                        }
                    ]
                }
                mock_get.return_value = mock_response
                
                # Simular workflow
                client = MeersensWaterClient()
                api_response = client.fetch(
                    latitude=Decimal("-23.5505"),
                    longitude=Decimal("-46.6333"),
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                )
                
                parser = WaterParser(mock_repo)
                readings = parser.parse(
                    station_id=1,
                    api_payload=api_response,
                )
                
                assert "values" in api_response
                assert isinstance(readings, list)

    def test_weather_workflow_fetch_and_parse(self):
        """Deve conseguir buscar e fazer parse de dados de clima."""
        mock_repo = MagicMock(spec=ReadingRepository)
        mock_repo._get_parameter_id_by_code.return_value = 1
        
        with patch('src.ingestion.weather_client.get_api_key') as mock_get_key:
            mock_get_key.return_value = "test_key"
            
            with patch('src.ingestion.weather_client.requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "values": [
                        {
                            "timestamp": "2026-01-15T10:30:00Z",
                            "temperature": 25.5,
                        }
                    ]
                }
                mock_get.return_value = mock_response
                
                # Simular workflow
                client = MeersensWeatherClient()
                api_response = client.fetch(
                    latitude=Decimal("-23.5505"),
                    longitude=Decimal("-46.6333"),
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                )
                
                parser = WeatherParser(mock_repo)
                readings = parser.parse(
                    station_id=1,
                    api_payload=api_response,
                )
                
                assert "values" in api_response
                assert isinstance(readings, list)
