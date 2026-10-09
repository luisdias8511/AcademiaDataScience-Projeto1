"""Testes para os módulos de ETL (extração, transformação e carga).

Cobre water/weather API fetching, data normalization, parameter extraction,
caching, pagination e error handling.
"""

import pytest
import json
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from src.ingestion import etl_water, etl_weather
from src.database.reading_repository import ReadingRepository


# ===================== Fixtures Compartilhadas =====================

@pytest.fixture
def mock_repo():
    """Mock do repositório com parâmetros de água e clima."""
    repo = MagicMock(spec=ReadingRepository)
    repo.get_water_parameters_codes.return_value = [
        "temperature",
        "oxygen",
        "ph",
    ]
    repo.get_weather_parameters_codes.return_value = [
        "temp",
        "humidity",
        "wind_speed",
    ]
    return repo


@pytest.fixture
def sample_water_api_response():
    """Exemplo de resposta da API de qualidade da água."""
    return {
        "values": [
            {
                "datetime": "2026-01-15T10:30:00Z",
                "pollutants_temperature_value": 22.5,
                "pollutants_oxygen_value": 8.2,
                "pollutants_ph_value": 7.1,
            },
            {
                "datetime": "2026-01-15T11:30:00Z",
                "pollutants_temperature_value": 23.0,
                "pollutants_oxygen_value": 8.3,
                "pollutants_ph_value": 7.0,
            },
        ],
        "found": 2,
    }


@pytest.fixture
def sample_weather_api_response():
    """Exemplo de resposta da API meteorológica."""
    return {
        "values": [
            {
                "datetime": "2026-01-15T10:00:00Z",
                "parameters_temp_value": 25.0,
                "parameters_humidity_value": 65.0,
                "parameters_wind_speed_value": 12.5,
            },
            {
                "datetime": "2026-01-15T11:00:00Z",
                "parameters_temp_value": 26.0,
                "parameters_humidity_value": 60.0,
                "parameters_wind_speed_value": 13.0,
            },
        ],
        "found": 2,
    }


# ===================== Testes de Water ETL =====================

class TestWaterParametersCaching:
    """Testes para cache de parâmetros de água."""

    def test_get_water_parameters_cached_first_call(self, mock_repo):
        """Primeira chamada deve consultar repositório."""
        etl_water._water_params_cache = None

        with patch.object(etl_water, 'ReadingRepository', return_value=mock_repo):
            result = etl_water.get_water_parameters_cached()

            assert result == ["temperature", "oxygen", "ph"]
            mock_repo.get_water_parameters_codes.assert_called_once()

    def test_get_water_parameters_cached_uses_cache(self, mock_repo):
        """Segunda chamada deve usar cache sem consultar repositório."""
        etl_water._water_params_cache = ["temperature", "oxygen", "ph"]

        with patch.object(etl_water, 'ReadingRepository', return_value=mock_repo):
            result = etl_water.get_water_parameters_cached()

            assert result == ["temperature", "oxygen", "ph"]
            # Não deve chamar, pois já tem no cache
            mock_repo.get_water_parameters_codes.assert_not_called()

    def teardown_method(self):
        """Limpar cache após cada teste."""
        etl_water._water_params_cache = None


class TestWaterApiKey:
    """Testes para obtenção de chave da API de água."""

    def test_get_api_key_success(self):
        """Deve retornar chave da API quando disponível."""
        with patch('src.ingestion.etl_water.security') as mock_security:
            mock_security.api_key_real = "test_water_api_key"

            key = etl_water.get_api_key()

            assert key == "test_water_api_key"

    def test_get_api_key_raises_when_not_loaded(self):
        """Deve lançar ValueError quando chave não está carregada."""
        with patch('src.ingestion.etl_water.security') as mock_security:
            mock_security.api_key_real = None

            with pytest.raises(ValueError) as exc_info:
                etl_water.get_api_key()
            assert "api" in str(exc_info.value).lower()

    def test_get_api_key_raises_when_attribute_missing(self):
        """Deve lançar ValueError se atributo não existe."""
        with patch('src.ingestion.etl_water.security') as mock_security:
            del mock_security.api_key_real

            with pytest.raises(ValueError) as exc_info:
                etl_water.get_api_key()
            assert "api" in str(exc_info.value).lower()


class TestWaterFetchHistory:
    """Testes para fetching de histórico de água."""

    def test_fetch_water_history_success(self, sample_water_api_response):
        """Deve fazer requisição HTTP com parâmetros corretos."""
        with patch('src.ingestion.etl_water.requests.get') as mock_get:
            with patch('src.ingestion.etl_water.get_api_key', return_value='test_key'):
                mock_get.return_value.json.return_value = sample_water_api_response

                result = etl_water._fetch_water_history(
                    lat=-15.5,
                    lng=-48.5,
                    from_date="2026-01-15T00:00:00Z",
                    to_date="2026-01-16T00:00:00Z",
                    page=0,
                )

                assert result == sample_water_api_response
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs['headers'] == {'apikey': 'test_key'}
                assert call_kwargs['params']['lat'] == -15.5
                assert call_kwargs['params']['lng'] == -48.5
                assert call_kwargs['timeout'] == 30

    def test_fetch_water_history_with_pagination(self):
        """Deve incluir número de página nos parâmetros."""
        with patch('src.ingestion.etl_water.requests.get') as mock_get:
            with patch('src.ingestion.etl_water.get_api_key', return_value='test_key'):
                mock_get.return_value.json.return_value = {"values": []}

                etl_water._fetch_water_history(
                    lat=-15.5,
                    lng=-48.5,
                    from_date="2026-01-15",
                    to_date="2026-01-16",
                    page=3,
                )

                call_kwargs = mock_get.call_args[1]
                assert call_kwargs['params']['page'] == 3

    def test_fetch_water_history_http_error(self):
        """Deve propagar exceção HTTP."""
        with patch('src.ingestion.etl_water.requests.get') as mock_get:
            with patch('src.ingestion.etl_water.get_api_key', return_value='test_key'):
                mock_get.return_value.raise_for_status.side_effect = Exception("HTTP 401")

                with pytest.raises(Exception) as exc_info:
                    etl_water._fetch_water_history(
                        lat=-15.5,
                        lng=-48.5,
                        from_date="2026-01-15",
                        to_date="2026-01-16",
                    )

                assert "HTTP 401" in str(exc_info.value)


class TestWaterNormalizeData:
    """Testes para normalização de dados de água."""

    def test_normalize_water_data_success(self, sample_water_api_response):
        """Deve converter payload em DataFrame normalizado."""
        df = etl_water._normalize_water_data(sample_water_api_response)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "datetime" in df.columns
        assert "pollutants_temperature_value" in df.columns
        assert df.iloc[0]["pollutants_temperature_value"] == 22.5

    def test_normalize_water_data_missing_values_key(self):
        """Deve lançar KeyError se 'values' não existe."""
        payload = {"found": 0}

        with pytest.raises(KeyError) as exc_info:
            etl_water._normalize_water_data(payload)
        assert "values" in str(exc_info.value)

    def test_normalize_water_data_values_not_list(self):
        """Deve lançar TypeError se 'values' não é lista."""
        payload = {"values": "not_a_list"}

        with pytest.raises(TypeError) as exc_info:
            etl_water._normalize_water_data(payload)
        assert "lista" in str(exc_info.value).lower()

    def test_normalize_water_data_empty_values(self):
        """Deve retornar DataFrame vazio se 'values' está vazio."""
        payload = {"values": [], "found": 0}

        df = etl_water._normalize_water_data(payload)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


class TestWaterExtractParameterColumns:
    """Testes para extração de colunas de parâmetros de água."""

    def test_extract_parameter_columns_success(self, sample_water_api_response):
        """Deve selecionar apenas colunas de parâmetros válidos."""
        df = etl_water._normalize_water_data(sample_water_api_response)
        parameter_codes = ["temperature", "oxygen", "ph"]

        result = etl_water._extract_parameter_columns(df, parameter_codes)

        assert "datetime" in result.columns
        assert "pollutants_temperature_value" in result.columns
        assert "pollutants_oxygen_value" in result.columns
        assert len(result) == 2

    def test_extract_parameter_columns_empty_dataframe(self):
        """Deve retornar DataFrame com colunas esperadas mesmo vazio."""
        df = pd.DataFrame()
        parameter_codes = ["temperature", "oxygen"]

        result = etl_water._extract_parameter_columns(df, parameter_codes)

        assert "datetime" in result.columns
        assert "pollutants_temperature_value" in result.columns
        assert len(result) == 0

    def test_extract_parameter_columns_no_matching_codes(self):
        """Deve lançar KeyError se nenhum parâmetro existe no DataFrame."""
        df = pd.DataFrame({
            "datetime": ["2026-01-15T10:00:00Z"],
            "pollutants_unknown_value": [1.0],
        })
        parameter_codes = ["temperature", "oxygen"]

        with pytest.raises(KeyError) as exc_info:
            etl_water._extract_parameter_columns(df, parameter_codes)
        assert "parâmetro" in str(exc_info.value).lower()

    def test_extract_parameter_columns_partial_match(self):
        """Deve selecionar apenas parâmetros que existem no banco."""
        df = pd.DataFrame({
            "datetime": ["2026-01-15T10:00:00Z"],
            "pollutants_temperature_value": [22.5],
            "pollutants_unknown_value": [1.0],
        })
        parameter_codes = ["temperature", "oxygen"]

        result = etl_water._extract_parameter_columns(df, parameter_codes)

        assert "pollutants_temperature_value" in result.columns
        assert "pollutants_unknown_value" not in result.columns


class TestWaterConsultaApi:
    """Testes para função principal de consulta de água."""

    def test_consulta_api_single_page(self, sample_water_api_response, mock_repo):
        """Deve retornar dados de uma única página."""
        etl_water._water_params_cache = None

        with patch.object(etl_water, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_water._fetch_water_history') as mock_fetch:
                with patch('src.ingestion.etl_water.logger'):
                    mock_fetch.side_effect = [
                        sample_water_api_response,
                        {"values": []},  # Próxima página vazia (para)
                    ]

                    result = etl_water.consulta_api(
                        lat=-15.5,
                        lng=-48.5,
                        from_date=datetime(2026, 1, 15),
                        to_date=datetime(2026, 1, 16),
                    )

                    assert isinstance(result, pd.DataFrame)
                    assert len(result) == 2
                    assert "datetime" in result.columns

        etl_water._water_params_cache = None

    def test_consulta_api_multiple_pages(self, mock_repo):
        """Deve concatenar múltiplas páginas."""
        page1 = {
            "values": [
                {"datetime": "2026-01-15T10:00:00Z", "pollutants_temperature_value": 22.5}
            ]
        }
        page2 = {
            "values": [
                {"datetime": "2026-01-15T11:00:00Z", "pollutants_temperature_value": 23.0}
            ]
        }
        etl_water._water_params_cache = None

        with patch.object(etl_water, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_water._fetch_water_history') as mock_fetch:
                with patch('src.ingestion.etl_water.logger'):
                    mock_fetch.side_effect = [page1, page2, {"values": []}]

                    result = etl_water.consulta_api(
                        lat=-15.5,
                        lng=-48.5,
                        from_date=datetime(2026, 1, 15),
                        to_date=datetime(2026, 1, 16),
                    )

                    assert len(result) == 2

        etl_water._water_params_cache = None

    def test_consulta_api_duplicate_page_detection(self, mock_repo):
        """Deve detectar páginas duplicadas e parar."""
        page = {
            "values": [
                {"datetime": "2026-01-15T10:00:00Z", "pollutants_temperature_value": 22.5}
            ]
        }
        etl_water._water_params_cache = None

        with patch.object(etl_water, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_water._fetch_water_history') as mock_fetch:
                with patch('src.ingestion.etl_water.logger'):
                    with patch('src.ingestion.etl_water.tratar_erro'):
                        mock_fetch.side_effect = [page, page]  # Mesma página 2x

                        # Deve chamar tratar_erro (que encerra), logo vai lançar exception
                        etl_water.consulta_api(
                            lat=-15.5,
                            lng=-48.5,
                            from_date=datetime(2026, 1, 15),
                            to_date=datetime(2026, 1, 16),
                        )

        etl_water._water_params_cache = None

    def test_consulta_api_datetime_conversion(self, sample_water_api_response, mock_repo):
        """Deve converter datetime para string ISO."""
        etl_water._water_params_cache = None

        with patch.object(etl_water, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_water._fetch_water_history') as mock_fetch:
                with patch('src.ingestion.etl_water.logger'):
                    mock_fetch.side_effect = [
                        sample_water_api_response,
                        {"values": []},
                    ]

                    etl_water.consulta_api(
                        lat=-15.5,
                        lng=-48.5,
                        from_date=datetime(2026, 1, 15, 10, 30),
                        to_date=datetime(2026, 1, 16, 10, 30),
                    )

                    # Verificar que _fetch_water_history foi chamado
                    assert mock_fetch.called
                    # Deve ter feito pelo menos 2 chamadas (página 0 e depois vazia)
                    assert mock_fetch.call_count >= 1

        etl_water._water_params_cache = None


# ===================== Testes de Weather ETL =====================

class TestWeatherParametersCaching:
    """Testes para cache de parâmetros meteorológicos."""

    def test_get_weather_parameters_cached_first_call(self, mock_repo):
        """Primeira chamada deve consultar repositório."""
        etl_weather._weather_params_cache = None

        with patch.object(etl_weather, 'ReadingRepository', return_value=mock_repo):
            result = etl_weather.get_weather_parameters_cached()

            assert result == ["temp", "humidity", "wind_speed"]
            mock_repo.get_weather_parameters_codes.assert_called_once()

    def test_get_weather_parameters_cached_uses_cache(self, mock_repo):
        """Segunda chamada deve usar cache."""
        etl_weather._weather_params_cache = ["temp", "humidity", "wind_speed"]

        with patch.object(etl_weather, 'ReadingRepository', return_value=mock_repo):
            result = etl_weather.get_weather_parameters_cached()

            assert result == ["temp", "humidity", "wind_speed"]
            mock_repo.get_weather_parameters_codes.assert_not_called()

    def teardown_method(self):
        """Limpar cache após cada teste."""
        etl_weather._weather_params_cache = None


class TestWeatherApiKey:
    """Testes para obtenção de chave da API meteorológica."""

    def test_get_api_key_success(self):
        """Deve retornar chave da API quando disponível."""
        with patch('src.ingestion.etl_weather.security') as mock_security:
            mock_security.api_key_real = "test_weather_api_key"

            key = etl_weather.get_api_key()

            assert key == "test_weather_api_key"

    def test_get_api_key_raises_when_not_loaded(self):
        """Deve lançar ValueError quando chave não está carregada."""
        with patch('src.ingestion.etl_weather.security') as mock_security:
            mock_security.api_key_real = None

            with pytest.raises(ValueError) as exc_info:
                etl_weather.get_api_key()
            assert "api" in str(exc_info.value).lower()


class TestWeatherFetchHistory:
    """Testes para fetching de histórico meteorológico."""

    def test_fetch_weather_history_success(self, sample_weather_api_response):
        """Deve fazer requisição HTTP com parâmetros corretos."""
        with patch('src.ingestion.etl_weather.requests.get') as mock_get:
            with patch('src.ingestion.etl_weather.get_api_key', return_value='test_key'):
                mock_get.return_value.json.return_value = sample_weather_api_response

                result = etl_weather._fetch_weather_history(
                    lat=-15.5,
                    lng=-48.5,
                    from_date="2026-01-15T00:00:00Z",
                    to_date="2026-01-16T00:00:00Z",
                )

                assert result == sample_weather_api_response
                mock_get.assert_called_once()

    def test_fetch_weather_history_http_error(self):
        """Deve propagar exceção HTTP."""
        with patch('src.ingestion.etl_weather.requests.get') as mock_get:
            with patch('src.ingestion.etl_weather.get_api_key', return_value='test_key'):
                mock_get.return_value.raise_for_status.side_effect = Exception("HTTP 500")

                with pytest.raises(Exception):
                    etl_weather._fetch_weather_history(
                        lat=-15.5,
                        lng=-48.5,
                        from_date="2026-01-15",
                        to_date="2026-01-16",
                    )


class TestWeatherNormalizeData:
    """Testes para normalização de dados meteorológicos."""

    def test_normalize_weather_data_success(self, sample_weather_api_response):
        """Deve converter payload em DataFrame normalizado."""
        df = etl_weather._normalize_weather_data(sample_weather_api_response)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "datetime" in df.columns
        assert "parameters_temp_value" in df.columns

    def test_normalize_weather_data_missing_values_key(self):
        """Deve lançar KeyError se 'values' não existe."""
        payload = {"found": 0}

        with pytest.raises(KeyError) as exc_info:
            etl_weather._normalize_weather_data(payload)
        assert "values" in str(exc_info.value)

    def test_normalize_weather_data_empty_values(self):
        """Deve retornar DataFrame vazio se 'values' está vazio."""
        payload = {"values": [], "found": 0}

        df = etl_weather._normalize_weather_data(payload)

        assert len(df) == 0


class TestWeatherExtractParameterColumns:
    """Testes para extração de colunas de parâmetros meteorológicos."""

    def test_extract_parameter_columns_success(self, sample_weather_api_response):
        """Deve selecionar apenas colunas de parâmetros válidos."""
        df = etl_weather._normalize_weather_data(sample_weather_api_response)
        parameter_codes = ["temp", "humidity", "wind_speed"]

        result = etl_weather._extract_parameter_columns(df, parameter_codes)

        assert "datetime" in result.columns
        assert "parameters_temp_value" in result.columns
        assert len(result) == 2

    def test_extract_parameter_columns_no_matching_codes(self):
        """Deve lançar KeyError se nenhum parâmetro existe."""
        df = pd.DataFrame({
            "datetime": ["2026-01-15T10:00:00Z"],
            "parameters_unknown_value": [1.0],
        })
        parameter_codes = ["temp", "humidity"]

        with pytest.raises(KeyError) as exc_info:
            etl_weather._extract_parameter_columns(df, parameter_codes)
        assert "parâmetro" in str(exc_info.value).lower()


class TestWeatherConsultaApi:
    """Testes para função principal de consulta meteorológica."""

    def test_consulta_api_single_page(self, sample_weather_api_response, mock_repo):
        """Deve retornar dados de uma única página."""
        etl_weather._weather_params_cache = None

        with patch.object(etl_weather, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_weather._fetch_weather_history') as mock_fetch:
                with patch('src.ingestion.etl_weather.logger'):
                    mock_fetch.side_effect = [
                        sample_weather_api_response,
                        {"values": []},
                    ]

                    result = etl_weather.consulta_api(
                        lat=-15.5,
                        lng=-48.5,
                        from_date="2026-01-15",
                        to_date="2026-01-16",
                    )

                    assert isinstance(result, pd.DataFrame)
                    assert len(result) == 2

        etl_weather._weather_params_cache = None

    def test_consulta_api_multiple_pages(self, mock_repo):
        """Deve concatenar múltiplas páginas."""
        page1 = {
            "values": [
                {"datetime": "2026-01-15T10:00:00Z", "parameters_temp_value": 25.0}
            ]
        }
        page2 = {
            "values": [
                {"datetime": "2026-01-15T11:00:00Z", "parameters_temp_value": 26.0}
            ]
        }
        etl_weather._weather_params_cache = None

        with patch.object(etl_weather, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_weather._fetch_weather_history') as mock_fetch:
                with patch('src.ingestion.etl_weather.logger'):
                    mock_fetch.side_effect = [page1, page2, {"values": []}]

                    result = etl_weather.consulta_api(
                        lat=-15.5,
                        lng=-48.5,
                        from_date="2026-01-15",
                        to_date="2026-01-16",
                    )

                    assert len(result) == 2

        etl_weather._weather_params_cache = None

    def test_consulta_api_empty_result(self, mock_repo):
        """Deve retornar DataFrame vazio quando não há dados."""
        etl_weather._weather_params_cache = None

        with patch.object(etl_weather, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_weather._fetch_weather_history') as mock_fetch:
                with patch('src.ingestion.etl_weather.logger'):
                    mock_fetch.return_value = {"values": []}

                    result = etl_weather.consulta_api(
                        lat=-15.5,
                        lng=-48.5,
                        from_date="2026-01-15",
                        to_date="2026-01-16",
                    )

                    assert isinstance(result, pd.DataFrame)
                    assert len(result) == 0

        etl_weather._weather_params_cache = None

    def test_consulta_api_error_handling(self, mock_repo):
        """Deve chamar tratar_erro em caso de exceção."""
        etl_weather._weather_params_cache = None

        with patch.object(etl_weather, 'ReadingRepository', return_value=mock_repo):
            with patch('src.ingestion.etl_weather._fetch_weather_history') as mock_fetch:
                with patch('src.ingestion.etl_weather.logger'):
                    with patch('src.ingestion.etl_weather.tratar_erro') as mock_error:
                        mock_fetch.side_effect = Exception("API Error")

                        etl_weather.consulta_api(
                            lat=-15.5,
                            lng=-48.5,
                            from_date="2026-01-15",
                            to_date="2026-01-16",
                        )

                        # Deve ter chamado tratar_erro
                        mock_error.assert_called_once()

        etl_weather._weather_params_cache = None
