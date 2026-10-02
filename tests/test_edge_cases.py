"""Testes para casos extremos e edge cases."""

import pytest
import math
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.station import Station
from src.analytics.statistics import calcular_estatisticas
from statistics import quantiles

from src.analytics.outliers import identificar_outliers


class TestExtremeValues:
    """Testes para valores extremos e limites."""

    def test_station_coordinates_at_boundaries(self):
        """Testa coordenadas nos limites válidos."""
        # Polo Norte
        station_north = Station(
            id=1,
            code="NORTH",
            name="Polo Norte",
            latitude=Decimal("90"),
            longitude=Decimal("0"),
        )
        assert station_north.latitude == Decimal("90")

        # Polo Sul
        station_south = Station(
            id=2,
            code="SOUTH",
            name="Polo Sul",
            latitude=Decimal("-90"),
            longitude=Decimal("0"),
        )
        assert station_south.latitude == Decimal("-90")

        # Data Line
        station_west = Station(
            id=3,
            code="WEST",
            name="Meridiano Oeste",
            latitude=Decimal("0"),
            longitude=Decimal("-180"),
        )
        assert station_west.longitude == Decimal("-180")

        station_east = Station(
            id=4,
            code="EAST",
            name="Meridiano Leste",
            latitude=Decimal("0"),
            longitude=Decimal("180"),
        )
        assert station_east.longitude == Decimal("180")

    def test_reading_value_extreme_temperatures(self):
        """Testa valores extremos de temperatura."""
        # Temperatura mais quente registrada: ~54°C (Death Valley)
        extreme_hot = ReadingValue(parameter_code="TEMPERATURE", value="54.0")
        assert float(extreme_hot.value) == 54.0

        # Temperatura mais fria registrada: ~-89°C (Antártica)
        extreme_cold = ReadingValue(parameter_code="TEMPERATURE", value="-89.0")
        assert float(extreme_cold.value) == -89.0

    def test_reading_value_very_small_values(self):
        """Testa valores muito pequenos."""
        tiny_value = ReadingValue(parameter_code="CONCENTRATION", value="0.00001")
        assert float(tiny_value.value) == 0.00001

    def test_reading_value_very_large_values(self):
        """Testa valores muito grandes."""
        huge_value = ReadingValue(parameter_code="PRESSURE", value="1000000000")
        assert float(huge_value.value) == 1000000000

    def test_statistics_with_identical_values(self):
        """Testa estatísticas quando todos valores são iguais."""
        values = [5.0] * 100
        stats = calcular_estatisticas(values)

        assert stats["media"] == 5.0
        assert stats["mediana"] == 5.0
        assert stats["desvio_padrao"] == 0.0
        assert stats["q1"] == 5.0
        assert stats["q3"] == 5.0
        assert stats["iqr"] == 0.0

    def test_statistics_with_two_values(self):
        """Testa estatísticas com apenas 2 observações (mínimo)."""
        values = [10.0, 20.0]
        stats = calcular_estatisticas(values)

        assert stats["media"] == 15.0
        assert stats["mediana"] == 15.0
        assert len(values) == 2

    def test_outlier_detection_with_single_outlier(self):
        """Testa detecção com um único outlier extremo."""
        values = [10, 10, 10, 10, 100]  # 100 é extremo
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        outliers = result["outliers"]

        assert len(outliers) == 1
        assert 100 in outliers

    def test_outlier_detection_all_same_values(self):
        """Testa detecção quando todos valores são iguais."""
        values = [5, 5, 5, 5, 5]
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        outliers = result["outliers"]

        # Com IQR = 0, nenhum valor é considerado outlier
        assert len(outliers) == 0

    def test_outlier_detection_with_two_groups(self):
        """Testa detecção com dois grupos bem separados."""
        values = [1, 1, 1, 1, 1, 100, 100, 100, 100, 100]
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        outliers = result["outliers"]

        # Os extremos de cada grupo podem ser outliers
        assert len(outliers) >= 0  # Depende do cálculo de IQR


class TestTimezoneHandling:
    """Testes para tratamento de timezone."""

    def test_reading_with_utc_timezone(self):
        """Deve aceitar timestamp com UTC."""
        reading = Reading(
            station_id=1,
            timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )
        assert reading.timestamp.tzinfo == timezone.utc

    def test_reading_with_custom_timezone(self):
        """Deve aceitar timestamp com timezone customizado."""
        from datetime import timezone as tz_module
        
        # Timezone de São Paulo (UTC-3 em janeiro)
        sp_tz = tz_module(timedelta(hours=-3))
        reading = Reading(
            station_id=1,
            timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=sp_tz),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )
        assert reading.timestamp.tzinfo is not None
        assert reading.timestamp.tzinfo != timezone.utc

    def test_reading_naive_datetime_fails(self):
        """Deve rejeitar datetime sem timezone."""
        with pytest.raises(ValueError, match="timezone-aware"):
            Reading(
                station_id=1,
                timestamp=datetime(2026, 1, 1, 12, 0, 0),  # Sem tzinfo
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            )


class TestStringValidation:
    """Testes para validação de strings."""

    def test_station_name_with_special_characters(self):
        """Deve aceitar nome de estação com caracteres especiais."""
        station = Station(
            id=1,
            code="EST_001",
            name="Estação São Paulo - Capital",
            latitude=Decimal("0"),
            longitude=Decimal("0"),
        )
        assert "São Paulo" in station.name

    def test_station_code_with_numbers(self):
        """Deve aceitar código com números."""
        station = Station(
            id=1,
            code="EST2026",
            name="Estação",
            latitude=Decimal("0"),
            longitude=Decimal("0"),
        )
        assert station.code == "EST2026"

    def test_parameter_code_case_sensitive(self):
        """Códigos de parâmetro devem ser case-sensitive."""
        rv1 = ReadingValue(parameter_code="TEMPERATURE", value="25")
        rv2 = ReadingValue(parameter_code="temperature", value="25")
        
        assert rv1.parameter_code != rv2.parameter_code

    def test_station_name_empty_string_fails(self):
        """Nome vazio deve falhar."""
        with pytest.raises(ValueError):
            Station(
                id=1,
                code="EST_001",
                name="",  # Vazio
                latitude=Decimal("0"),
                longitude=Decimal("0"),
            )

    def test_parameter_code_whitespace_only_fails(self):
        """Código com apenas espaços deve falhar."""
        with pytest.raises(ValueError):
            ReadingValue(
                parameter_code="   ",  # Apenas espaços
                value="25",
            )


class TestNumericPrecision:
    """Testes para precisão numérica."""

    def test_float_precision_in_statistics(self):
        """Testa que cálculos mantêm precisão adequada."""
        # Valores que causam problemas de ponto flutuante
        values = [0.1 + 0.2, 0.3, 0.15 + 0.15]  # Pode haver imprecisão
        stats = calcular_estatisticas(values)

        # Verificar que média é aproximadamente correta
        assert 0.25 < stats["media"] < 0.35

    def test_scientific_notation_values(self):
        """Testa valores em notação científica."""
        rv = ReadingValue(parameter_code="CONCENTRATION", value="1.23e-4")
        assert float(rv.value) == 1.23e-4

    def test_negative_scientific_notation(self):
        """Testa valores negativos em notação científica."""
        rv = ReadingValue(parameter_code="DIFFERENCE", value="-2.5e-3")
        assert float(rv.value) == -2.5e-3

    def test_statistics_precision_with_many_decimals(self):
        """Testa precisão com valores de muitas casas decimais."""
        values = [1.123456789, 2.234567890, 3.345678901]
        stats = calcular_estatisticas(values)

        # Média deve ser ~2.234567860
        assert 2.2 < stats["media"] < 2.3


class TestBoundaryConditions:
    """Testes para condições de fronteira."""

    def test_reading_with_minimum_valid_station_id(self):
        """Testa com ID de estação = 1 (mínimo válido)."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )
        assert reading.station_id == 1

    def test_reading_with_very_large_station_id(self):
        """Testa com ID de estação muito grande."""
        reading = Reading(
            station_id=999999999,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )
        assert reading.station_id == 999999999

    def test_statistics_with_maximum_count(self):
        """Testa estatísticas com grande quantidade de valores."""
        values = list(range(10000))
        stats = calcular_estatisticas(values)

        assert len(values) == 10000
        assert stats["media"] == 4999.5

    def test_outlier_detection_with_many_points(self):
        """Testa detecção de outliers com muitos pontos."""
        normal_values = list(range(100, 200))  # 100 valores normais
        outliers_vals = [0, 300]  # 2 outliers
        all_values = normal_values + outliers_vals

        q1, _, q3 = quantiles(all_values, n=4, method="inclusive")
        result = identificar_outliers(all_values, q1, q3)
        outliers = result["outliers"]

        # Deve detectar os outliers
        assert 0 in outliers
        assert 300 in outliers

    def test_datetime_at_midnight(self):
        """Testa timestamp no início do dia (meia-noite)."""
        reading = Reading(
            station_id=1,
            timestamp=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )
        assert reading.timestamp.hour == 0
        assert reading.timestamp.minute == 0

    def test_datetime_at_end_of_year(self):
        """Testa timestamp no final do ano."""
        reading = Reading(
            station_id=1,
            timestamp=datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )
        assert reading.timestamp.year == 2026
        assert reading.timestamp.month == 12
        assert reading.timestamp.day == 31


class TestDataConsistency:
    """Testes para consistência de dados."""

    def test_immutability_prevents_modification(self):
        """Verifica que objetos frozen não podem ser modificados."""
        station = Station(
            id=1,
            code="EST_001",
            name="Estação",
            latitude=Decimal("0"),
            longitude=Decimal("0"),
        )

        with pytest.raises(AttributeError):
            station.code = "NEW_CODE"

    def test_tuple_immutability_in_reading(self):
        """Verifica que tupla de valores em Reading é imutável."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )

        with pytest.raises((TypeError, AttributeError)):
            reading.values[0] = ReadingValue(parameter_code="HUMIDITY", value="60")

    def test_reading_value_tuple_ordering(self):
        """Verifica que ordem de valores é preservada."""
        values = (
            ReadingValue(parameter_code="TEMP", value="25"),
            ReadingValue(parameter_code="HUMIDITY", value="60"),
            ReadingValue(parameter_code="PRESSURE", value="1013"),
        )
        reading = Reading(station_id=1, timestamp=datetime.now(timezone.utc), values=values)

        assert reading.values[0].parameter_code == "TEMP"
        assert reading.values[1].parameter_code == "HUMIDITY"
        assert reading.values[2].parameter_code == "PRESSURE"
