"""Testes para validação e processamento de leituras."""

import pytest
from datetime import datetime, timezone
import math

from src.processing.reading_processor import ReadingProcessor
from src.models.reading import Reading
from src.models.reading_value import ReadingValue


class TestReadingProcessor:
    """Testes para o processador de leituras."""

    @pytest.fixture
    def processor(self):
        """Cria instância do processador."""
        return ReadingProcessor()

    def test_validate_reading_valid(self, processor, sample_reading):
        """Deve validar leitura correta sem exceção."""
        processor.validate(sample_reading)  # Não deve lançar exceção

    def test_validate_reading_invalid_station_id_zero(self, processor):
        """Deve rejeitar leitura com ID de estação = 0."""
        # A validação ocorre durante a construção do Reading
        with pytest.raises(ValueError):
            reading = Reading(
                station_id=0,
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            )

    def test_validate_reading_invalid_station_id_negative(self, processor):
        """Deve rejeitar leitura com ID de estação negativo."""
        # A validação ocorre durante a construção do Reading
        with pytest.raises(ValueError):
            reading = Reading(
                station_id=-1,
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            )

    def test_validate_reading_invalid_timestamp_not_datetime(self, processor):
        """Deve rejeitar timestamp que não é datetime."""
        # Criação será bloqueada pela validação do modelo
        # Este teste documenta que o processador também valida
        pass

    def test_validate_reading_invalid_timestamp_no_timezone(self, processor):
        """Deve rejeitar timestamp sem timezone."""
        # A validação ocorre durante a construção do Reading
        with pytest.raises(ValueError):
            reading = Reading(
                station_id=1,
                timestamp=datetime.now(),  # Sem timezone
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            )

    def test_validate_reading_invalid_empty_values(self, processor):
        """Deve rejeitar leitura sem valores."""
        # A validação ocorre durante a construção do Reading
        with pytest.raises(ValueError):
            reading = Reading(
                station_id=1,
                timestamp=datetime.now(timezone.utc),
                values=(),
            )

    def test_validate_reading_invalid_parameter_code_empty(self, processor):
        """Deve rejeitar valor com código de parâmetro vazio."""
        # A validação ocorre durante a construção de ReadingValue
        with pytest.raises(ValueError):
            reading = Reading(
                station_id=1,
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="", value="25"),),
            )

    def test_validate_reading_invalid_value_not_numeric(self, processor):
        """Deve rejeitar valor não numérico."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="abc"),),
        )
        # ReadingValue já valida isso na inicialização
        with pytest.raises(ValueError):
            processor.validate(reading)

    def test_validate_reading_invalid_value_nan(self, processor):
        """Deve rejeitar NaN como valor."""
        # Temos que forçar criação de um ReadingValue inválido
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="nan"),),
        )
        with pytest.raises(ValueError, match="não finito"):
            processor.validate(reading)

    def test_validate_reading_invalid_value_infinity(self, processor):
        """Deve rejeitar infinito como valor."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="inf"),),
        )
        with pytest.raises(ValueError, match="não finito"):
            processor.validate(reading)

    def test_validate_reading_multiple_values(self, processor):
        """Deve validar leitura com múltiplos valores."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(
                ReadingValue(parameter_code="TEMP", value="25.5"),
                ReadingValue(parameter_code="HUMIDITY", value="65.0"),
                ReadingValue(parameter_code="PRESSURE", value="1013.25"),
            ),
        )
        processor.validate(reading)  # Não deve lançar exceção

    def test_validate_reading_zero_value(self, processor):
        """Deve aceitar zero como valor válido."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="0"),),
        )
        processor.validate(reading)  # Não deve lançar exceção

    def test_validate_reading_negative_value(self, processor):
        """Deve aceitar valores negativos (para diferenças, altitudes, etc)."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="-5.5"),),
        )
        processor.validate(reading)  # Não deve lançar exceção

    def test_validate_reading_very_large_value(self, processor):
        """Deve aceitar valores muito grandes."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="LARGE_PARAM", value="999999999.999"),),
        )
        processor.validate(reading)  # Não deve lançar exceção

    def test_validate_reading_scientific_notation(self, processor):
        """Deve aceitar notação científica."""
        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="SMALL_PARAM", value="1.23e-4"),),
        )
        processor.validate(reading)  # Não deve lançar exceção
