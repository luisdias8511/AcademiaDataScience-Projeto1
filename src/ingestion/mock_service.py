"""Serviço de ingestion mock para demonstração."""

from datetime import datetime, timedelta
from decimal import Decimal

from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.station import Station


class MockIngestionService:
    """Simula um serviço de ingestão de dados sem chamar APIs reais."""

    def __init__(self):
        """Inicializa o serviço de ingestion mock."""
        pass

    def get_readings(
        self,
        station: Station,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Reading]:
        """Retorna uma lista fixa de readings para demonstração.
        
        Args:
            station: Estação selecionada
            start_date: Data inicial do período
            end_date: Data final do período
            
        Returns:
            Lista com 2 readings fixos contendo todos os parâmetros
        """
        # Gerar dois readings com timestamps diferentes dentro do período
        timestamp_1 = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        timestamp_2 = timestamp_1 + timedelta(hours=12)

        reading_1 = Reading(
            station_id=station.id,
            timestamp=timestamp_1,
            values=(
                ReadingValue(
                    parameter_code="temperature",
                    value=Decimal("21.06"),
                    unit="°C",
                ),
                ReadingValue(
                    parameter_code="humidity",
                    value=Decimal("65.50"),
                    unit="%",
                ),
                ReadingValue(
                    parameter_code="pressure",
                    value=Decimal("1013.25"),
                    unit="hPa",
                ),
                ReadingValue(
                    parameter_code="wind_speed",
                    value=Decimal("12.40"),
                    unit="m/s",
                ),
            ),
        )

        reading_2 = Reading(
            station_id=station.id,
            timestamp=timestamp_2,
            values=(
                ReadingValue(
                    parameter_code="temperature",
                    value=Decimal("22.15"),
                    unit="°C",
                ),
                ReadingValue(
                    parameter_code="humidity",
                    value=Decimal("63.20"),
                    unit="%",
                ),
                ReadingValue(
                    parameter_code="pressure",
                    value=Decimal("1012.80"),
                    unit="hPa",
                ),
                ReadingValue(
                    parameter_code="wind_speed",
                    value=Decimal("11.90"),
                    unit="m/s",
                ),
            ),
        )

        return [reading_1, reading_2]
