"""Processamento de leituras - validação e limpeza."""

import logging
import math
from collections.abc import Sequence
from datetime import datetime

from src.models.reading import Reading
from src.models.reading_value import ReadingValue

logger = logging.getLogger(__name__)


class ReadingProcessor:
    """Valida e limpa leituras em uma única classe.
    
    Responsabilidades:
    - Validar invariantes de Reading
    - Remover valores inválidos
    - Remover leituras sem dados válidos
    - Preparar dados para persistência
    """

    def validate(self, reading: Reading) -> None:
        """Valida uma leitura. Retorna None se válida, lança ValueError se inválida."""
        if reading.station_id <= 0:
            raise ValueError("O identificador da estação deve ser maior que zero.")

        if not isinstance(reading.timestamp, datetime):
            raise ValueError("O timestamp deve ser um objeto datetime.")

        if reading.timestamp.tzinfo is None:
            raise ValueError("O timestamp deve ser timezone-aware.")

        if not reading.values:
            raise ValueError("Uma leitura deve conter pelo menos um valor.")

        for reading_value in reading.values:
            if not reading_value.parameter_code:
                raise ValueError("O código do parâmetro não pode estar vazio.")

            try:
                value_float = float(reading_value.value)
                if not math.isfinite(value_float):
                    raise ValueError(
                        f"Valor não finito para parâmetro {reading_value.parameter_code}: {value_float}."
                    )
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Valor não numérico para parâmetro {reading_value.parameter_code}: {e}."
                )

        logger.debug(
            "Leitura validada com sucesso para estação %d e timestamp %s.",
            reading.station_id,
            reading.timestamp,
        )

    def clean(
        self,
        readings: Sequence[Reading],
    ) -> list[Reading]:
        """Remove leituras e valores inválidos."""
        cleaned_readings: list[Reading] = []

        for reading in readings:
            valid_values: list[ReadingValue] = []

            for reading_value in reading.values:
                # Verifica se valor é finito
                try:
                    value_float = float(reading_value.value)
                    if not math.isfinite(value_float):
                        logger.debug(
                            "Valor não finito ignorado para parâmetro %s: %s.",
                            reading_value.parameter_code,
                            value_float,
                        )
                        continue
                except (ValueError, TypeError):
                    logger.debug(
                        "Valor não numérico ignorado para parâmetro %s.",
                        reading_value.parameter_code,
                    )
                    continue

                valid_values.append(reading_value)

            # Se houver valores válidos, adiciona leitura
            if valid_values:
                if len(valid_values) == len(reading.values):
                    cleaned_readings.append(reading)
                else:
                    cleaned_reading = Reading(
                        station_id=reading.station_id,
                        timestamp=reading.timestamp,
                        values=tuple(valid_values),
                    )
                    cleaned_readings.append(cleaned_reading)
            else:
                logger.debug(
                    "Leitura descartada: nenhum valor válido para estação %d.",
                    reading.station_id,
                )

        return cleaned_readings
