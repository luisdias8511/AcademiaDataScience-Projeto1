"""Configuração compartilhada e fixtures para todos os testes."""

import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.models.station import Station
from src.models.parameter import Parameter
from src.models.reading_value import ReadingValue
from src.models.reading import Reading


@pytest.fixture
def sample_station():
    """Cria uma estação de teste."""
    return Station(
        id=1,
        code="EST_001",
        name="Estação Central",
        latitude=Decimal("-23.5505"),
        longitude=Decimal("-46.6333"),
    )


@pytest.fixture
def sample_parameter_weather():
    """Cria um parâmetro meteorológico para testes."""
    return Parameter(
        id=1,
        code="TEMPERATURE",
        code_api="temperature",
        name="Temperatura",
        unit="°C",
        category_id=1,
    )


@pytest.fixture
def sample_parameter_water():
    """Cria um parâmetro de água para testes."""
    return Parameter(
        id=2,
        code="PH",
        code_api="ph",
        name="pH",
        unit="",
        category_id=2,
    )


@pytest.fixture
def sample_reading_values():
    """Cria valores de leitura para testes."""
    return (
        ReadingValue(parameter_code="TEMPERATURE", value="25.5"),
        ReadingValue(parameter_code="HUMIDITY", value="65.0"),
    )


@pytest.fixture
def sample_reading(sample_reading_values):
    """Cria uma leitura completa para testes."""
    return Reading(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        values=sample_reading_values,
    )


@pytest.fixture
def sample_readings_list(sample_reading):
    """Cria múltiplas leituras para testes de análise."""
    base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    readings = []
    
    for i in range(10):
        timestamp = base_time + timedelta(days=i)
        values = (
            ReadingValue(parameter_code="TEMPERATURE", value=str(20.0 + i * 0.5)),
            ReadingValue(parameter_code="HUMIDITY", value=str(60.0 + i)),
        )
        readings.append(
            Reading(
                station_id=1,
                timestamp=timestamp,
                values=values,
            )
        )
    
    return readings


@pytest.fixture
def sample_readings_with_outliers():
    """Cria leituras com alguns outliers para teste de detecção."""
    base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    readings = []
    
    # Valores normais
    normal_values = [20.0, 21.0, 20.5, 21.5, 20.8, 21.2, 20.9, 21.1, 20.7, 21.3]
    # Adicionar outliers
    normal_values.extend([50.0, 55.0])  # Valores extremos
    
    for i, temp_value in enumerate(normal_values):
        timestamp = base_time + timedelta(days=i)
        values = (
            ReadingValue(parameter_code="TEMPERATURE", value=str(temp_value)),
        )
        readings.append(
            Reading(
                station_id=1,
                timestamp=timestamp,
                values=values,
            )
        )
    
    return readings
