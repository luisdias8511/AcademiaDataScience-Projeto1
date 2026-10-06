"""Testes para funções de suporte do Streamlit."""

import pytest
from datetime import date, timedelta, datetime, timezone
from unittest.mock import MagicMock, patch

from src.presentation.streamlit_support import (
    statistics_to_rows,
    validate_date_range,
)
from src.models.statistics_result import StatisticsResult
from src.models.parameter import Parameter
from src.analytics.service import AnalyticsService
from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from decimal import Decimal


class TestStatisticsToRows:
    """Testes para conversão de StatisticsResult em linhas de tabela."""

    def test_statistics_to_rows_with_parameter_name(self):
        """Deve exibir nome do parâmetro quando disponível."""
        statistics = [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                parameter_name="Temperatura",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(10.0, 35.0),
            ),
        ]

        rows = statistics_to_rows(statistics)

        assert len(rows) == 1
        assert rows[0]["Parâmetro"] == "Temperatura"
        assert rows[0]["Quantidade"] == 10
        assert rows[0]["Média"] == "22.50"
        assert rows[0]["Mediana"] == "22.00"
        assert rows[0]["Quantidade de outliers"] == 2

    def test_statistics_to_rows_without_parameter_name(self):
        """Deve exibir código quando nome não disponível."""
        statistics = [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(),
            ),
        ]

        rows = statistics_to_rows(statistics)

        assert len(rows) == 1
        assert rows[0]["Parâmetro"] == "TEMPERATURE"
        assert rows[0]["Quantidade de outliers"] == 0

    def test_statistics_to_rows_multiple_parameters(self):
        """Deve exibir múltiplos parâmetros com seus nomes."""
        statistics = [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                parameter_name="Temperatura",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(),
            ),
            StatisticsResult(
                parameter_code="HUMIDITY",
                parameter_name="Umidade",
                count=10,
                average=65.0,
                median=64.5,
                standard_deviation=5.0,
                q1=60.0,
                q3=70.0,
                iqr=10.0,
                lower_bound=45.0,
                upper_bound=85.0,
                outliers=(),
            ),
        ]

        rows = statistics_to_rows(statistics)

        assert len(rows) == 2
        assert rows[0]["Parâmetro"] == "Temperatura"
        assert rows[1]["Parâmetro"] == "Umidade"

    def test_statistics_to_rows_formatting(self):
        """Deve formatar valores com 2 casas decimais."""
        statistics = [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=10,
                average=22.12345,
                median=22.98765,
                standard_deviation=2.55555,
                q1=20.11111,
                q3=25.99999,
                iqr=5.88888,
                lower_bound=12.77777,
                upper_bound=32.33333,
                outliers=(),
            ),
        ]

        rows = statistics_to_rows(statistics)

        assert rows[0]["Média"] == "22.12"
        assert rows[0]["Mediana"] == "22.99"
        assert rows[0]["Desvio padrão"] == "2.56"
        assert rows[0]["Q1"] == "20.11"
        assert rows[0]["Q3"] == "26.00"


class TestValidateDateRange:
    """Testes para validação de intervalo de datas."""

    def test_validate_date_range_valid(self):
        """Deve validar intervalo de datas válido."""
        today = date.today()
        start = today - timedelta(days=30)
        end = today - timedelta(days=1)

        result = validate_date_range(start, end)

        assert result is None

    def test_validate_date_range_end_before_start(self):
        """Deve rejeitar quando data final é anterior à inicial."""
        today = date.today()
        start = today - timedelta(days=1)
        end = today - timedelta(days=30)

        result = validate_date_range(start, end)

        assert result is not None
        assert "data final deve ser maior" in result.lower()

    def test_validate_date_range_equal_dates(self):
        """Deve rejeitar quando datas são iguais."""
        today = date.today()
        start = today - timedelta(days=10)

        result = validate_date_range(start, start)

        assert result is not None
        # A primeira validação é se final > inicial, portanto essa mensagem aparece
        assert "data final deve ser maior" in result.lower()

    def test_validate_date_range_start_too_old(self):
        """Deve rejeitar data inicial muito antiga."""
        today = date.today()
        start = today - timedelta(days=100)
        end = today - timedelta(days=1)

        result = validate_date_range(start, end)

        assert result is not None
        assert "90 dias" in result.lower()

    def test_validate_date_range_end_is_today(self):
        """Deve rejeitar data final como hoje."""
        today = date.today()
        start = today - timedelta(days=10)

        result = validate_date_range(start, today)

        assert result is not None
        assert "ontem" in result.lower()

    def test_validate_date_range_end_future(self):
        """Deve rejeitar data final no futuro."""
        today = date.today()
        start = today - timedelta(days=10)
        end = today + timedelta(days=5)

        result = validate_date_range(start, end)

        assert result is not None
        # Verifica se é no máximo ontem (a validação de data futura vem depois)
        assert "no máximo ontem" in result.lower() or "futuras não são permitidas" in result.lower()


class TestAnalyticsServiceWithParameterNames:
    """Testes para integração entre AnalyticsService e nomes de parâmetros."""

    def test_analytics_service_includes_parameter_names(self):
        """Deve incluir nomes de parâmetros nos resultados estatísticos."""
        # Criar mock do repositório
        mock_repo = MagicMock()
        mock_repo.get_parameter_by_code.side_effect = lambda code: Parameter(
            id=1 if code == "TEMPERATURE" else 2,
            code=code,
            code_api=code,
            name="Temperatura" if code == "TEMPERATURE" else "Umidade",
            unit="°C" if code == "TEMPERATURE" else "%",
            category_id=1,
        )

        # Criar dados de teste
        readings = [
            Reading(
                station_id=1,
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                values=(
                    ReadingValue("TEMPERATURE", Decimal("20.0")),
                    ReadingValue("HUMIDITY", Decimal("60.0")),
                ),
            ),
            Reading(
                station_id=1,
                timestamp=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
                values=(
                    ReadingValue("TEMPERATURE", Decimal("22.0")),
                    ReadingValue("HUMIDITY", Decimal("65.0")),
                ),
            ),
        ]

        # Usar AnalyticsService com repositório
        service = AnalyticsService(repository=mock_repo)
        results = service.calculate(readings)

        # Verificar que os resultados incluem nomes
        assert len(results) == 2
        
        temp_result = next(r for r in results if r.parameter_code == "TEMPERATURE")
        humidity_result = next(r for r in results if r.parameter_code == "HUMIDITY")
        
        assert temp_result.parameter_name == "Temperatura"
        assert humidity_result.parameter_name == "Umidade"

    def test_statistics_to_rows_integration_with_analytics_service(self):
        """Deve exibir nomes dos parâmetros quando fornecidos pelo AnalyticsService."""
        # Criar mock do repositório
        mock_repo = MagicMock()
        mock_repo.get_parameter_by_code.side_effect = lambda code: Parameter(
            id=1,
            code=code,
            code_api=code,
            name="Temperatura do Ar",
            unit="°C",
            category_id=1,
        )

        # Criar dados de teste
        readings = [
            Reading(
                station_id=1,
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                values=(ReadingValue("TEMPERATURE", Decimal("20.0")),),
            ),
            Reading(
                station_id=1,
                timestamp=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
                values=(ReadingValue("TEMPERATURE", Decimal("22.0")),),
            ),
        ]

        # Fluxo completo
        service = AnalyticsService(repository=mock_repo)
        results = service.calculate(readings)
        rows = statistics_to_rows(results)

        # Verificar que a tabela usa o nome
        assert len(rows) == 1
        assert rows[0]["Parâmetro"] == "Temperatura do Ar"

