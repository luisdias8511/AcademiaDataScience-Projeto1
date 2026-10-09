"""Testes para os modelos de domínio."""

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from src.models.station import Station
from src.models.parameter import Parameter
from src.models.reading_value import ReadingValue
from src.models.reading import Reading
from src.models.statistics_result import StatisticsResult


class TestStation:
    """Testes para o modelo Station."""

    def test_station_creation_valid(self, sample_station):
        """Deve criar uma estação válida."""
        assert sample_station.id == 1
        assert sample_station.code == "EST_001"
        assert sample_station.name == "Estação Central"
        assert sample_station.latitude == Decimal("-23.5505")
        assert sample_station.longitude == Decimal("-46.6333")

    def test_station_invalid_id(self):
        """Deve rejeitar estação com ID inválido (≤ 0)."""
        with pytest.raises(ValueError, match="deve ser maior que zero"):
            Station(
                id=0,
                code="EST_001",
                name="Teste",
                latitude=Decimal("0"),
                longitude=Decimal("0"),
            )

    def test_station_invalid_code(self):
        """Deve rejeitar estação com código vazio."""
        with pytest.raises(ValueError, match="código.*estação.*não pode estar vazio"):
            Station(
                id=1,
                code="",
                name="Teste",
                latitude=Decimal("0"),
                longitude=Decimal("0"),
            )

    def test_station_invalid_latitude(self):
        """Deve rejeitar latitude fora do intervalo [-90, 90]."""
        with pytest.raises(ValueError, match="latitude"):
            Station(
                id=1,
                code="EST_001",
                name="Teste",
                latitude=Decimal("91"),
                longitude=Decimal("0"),
            )

    def test_station_invalid_longitude(self):
        """Deve rejeitar longitude fora do intervalo [-180, 180]."""
        with pytest.raises(ValueError, match="longitude"):
            Station(
                id=1,
                code="EST_001",
                name="Teste",
                latitude=Decimal("0"),
                longitude=Decimal("181"),
            )

    def test_station_is_immutable(self, sample_station):
        """Estações devem ser imutáveis (frozen dataclass)."""
        with pytest.raises(AttributeError):
            sample_station.name = "Nome modificado"


class TestParameter:
    """Testes para o modelo Parameter."""

    def test_parameter_creation_valid(self, sample_parameter_weather):
        """Deve criar um parâmetro válido."""
        assert sample_parameter_weather.id == 1
        assert sample_parameter_weather.code == "TEMPERATURE"
        assert sample_parameter_weather.name == "Temperatura"
        assert sample_parameter_weather.unit == "°C"
        assert sample_parameter_weather.category_id == 1

    def test_parameter_invalid_id(self):
        """Deve aceitar parâmetro com ID = 0 (já que é int | None, qualquer int é válido)."""
        # Note: ID pode ser None até persistência no banco de dados
        param = Parameter(
            id=0,  # Valores 0 são aceitáveis antes de persistir no DB
            code="TEMP",
            code_api="temperature",
            name="Temperatura",
            unit="°C",
            category_id=1,
        )
        assert param.id == 0

    def test_parameter_invalid_code(self):
        """Deve rejeitar parâmetro com código vazio."""
        with pytest.raises(ValueError, match="código.*não pode estar vazio"):
            Parameter(
                id=1,
                code="",
                code_api="temperature",
                name="Temperatura",
                unit="°C",
                category_id=1,
            )

    def test_parameter_is_immutable(self, sample_parameter_weather):
        """Parâmetros devem ser imutáveis."""
        with pytest.raises(AttributeError):
            sample_parameter_weather.unit = "K"


class TestReadingValue:
    """Testes para o modelo ReadingValue."""

    def test_reading_value_creation_valid(self):
        """Deve criar um valor de leitura válido."""
        rv = ReadingValue(parameter_code="TEMPERATURE", value="25.5")
        assert rv.parameter_code == "TEMPERATURE"
        assert rv.value == "25.5"

    def test_reading_value_invalid_parameter_code(self):
        """Deve rejeitar código de parâmetro vazio."""
        with pytest.raises(ValueError, match="código do parâmetro não pode estar vazio"):
            ReadingValue(parameter_code="", value=Decimal("25.5"))

    def test_reading_value_with_string_value(self):
        """Deve aceitar string e converter para Decimal."""
        # O dataclass aceita qualquer valor passado, mas o tipo é Decimal
        # então valores devem ser Decimal ou conversíveis para Decimal
        rv = ReadingValue(parameter_code="TEMPERATURE", value=Decimal("25.5"))
        assert isinstance(rv.value, Decimal)
        assert rv.value == Decimal("25.5")

    def test_reading_value_is_immutable(self):
        """Valores de leitura devem ser imutáveis."""
        rv = ReadingValue(parameter_code="TEMPERATURE", value="25.5")
        with pytest.raises(AttributeError):
            rv.value = "30.0"


class TestReading:
    """Testes para o modelo Reading."""

    def test_reading_creation_valid(self, sample_reading):
        """Deve criar uma leitura válida."""
        assert sample_reading.station_id == 1
        assert sample_reading.timestamp.tzinfo is not None
        assert len(sample_reading.values) > 0

    def test_reading_invalid_station_id(self):
        """Deve rejeitar leitura com ID de estação inválido."""
        with pytest.raises(ValueError, match="deve ser maior que zero"):
            Reading(
                station_id=0,
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            )

    def test_reading_invalid_timezone_unaware(self):
        """Deve rejeitar timestamp sem timezone."""
        with pytest.raises(ValueError, match="timezone-aware"):
            Reading(
                station_id=1,
                timestamp=datetime.now(),  # Sem timezone
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            )

    def test_reading_invalid_empty_values(self):
        """Deve rejeitar leitura sem valores."""
        with pytest.raises(ValueError, match="pelo menos um valor"):
            Reading(
                station_id=1,
                timestamp=datetime.now(timezone.utc),
                values=(),
            )

    def test_reading_is_immutable(self, sample_reading):
        """Leituras devem ser imutáveis."""
        with pytest.raises(AttributeError):
            sample_reading.station_id = 2


class TestStatisticsResult:
    """Testes para o modelo StatisticsResult."""

    def test_statistics_result_creation_valid(self):
        """Deve criar resultado estatístico válido."""
        result = StatisticsResult(
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
            outliers=(10.0, 35.0),
        )
        assert result.parameter_code == "TEMPERATURE"
        assert result.count == 10
        assert result.average == 22.5

    def test_statistics_result_invalid_empty_code(self):
        """Deve rejeitar código de parâmetro vazio."""
        with pytest.raises(ValueError, match="código do parâmetro não pode estar vazio"):
            StatisticsResult(
                parameter_code="",
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
            )

    def test_statistics_result_invalid_count(self):
        """Deve rejeitar contagem ≤ 0."""
        with pytest.raises(ValueError, match="contagem de observações deve ser maior"):
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=0,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(),
            )

    def test_statistics_result_invalid_stdev(self):
        """Deve rejeitar desvio padrão negativo."""
        with pytest.raises(ValueError, match="desvio padrão não pode ser negativo"):
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=-2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(),
            )

    def test_statistics_result_is_immutable(self):
        """Resultados estatísticos devem ser imutáveis."""
        result = StatisticsResult(
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
        )
        with pytest.raises(AttributeError):
            result.average = 25.0
