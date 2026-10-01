"""Serviço de ingestion na base de dados."""

from datetime import datetime, timedelta
from decimal import Decimal

from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.station import Station
from src.config import logger
from src.security.log_utils import tratar_erro


class IngestionService:
    """Serviço de ingestão de dados meteorológicos e de qualidade da água."""

    def __init__(self):
        """Inicializa o serviço de ingestion."""
        pass

    def fetch_weather_readings(
        self,
        station: Station,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Reading]:
        """Busca leituras na API e converte os valores em objetos de domínio."""
        logger.info(
            "Iniciando ingestão para estação %s no período %s a %s.",
            station.id,
            start_date,
            end_date,
        )
        try:
            import pandas as pd

            from src.ingestion.etl_weather import consulta_api

            api_readings = consulta_api(
                lat=float(station.latitude),
                lng=float(station.longitude),
                from_date=start_date,
                to_date=end_date,
            )

            if "datetime" not in api_readings.columns:
                raise KeyError("A resposta da API não contém a coluna 'datetime'.")

            readings: list[Reading] = []

            for _, row in api_readings.iterrows():
                values = tuple(
                    ReadingValue(
                        parameter_code=column[len("parameters_") : -len("_value")],
                        value=Decimal(str(row[column])),
                    )
                    for column in api_readings.columns
                    if column.startswith("parameters_")
                    and column.endswith("_value")
                    if not pd.isna(row[column])
                )

                if values:
                    readings.append(
                        Reading(
                            station_id=station.id,
                            timestamp=pd.to_datetime(row["datetime"]).to_pydatetime(),
                            values=values,
                        )
                    )

            logger.info(
                "Ingestão concluída para estação %s: %d leitura(s) coletada(s).",
                station.id,
                len(readings),
            )
            return readings
        except Exception as e:
            tratar_erro(
                e,
                f"Falha na ingestão de dados meteorológicos para estação {station.id}",
                encerrar=True,
            )

    def get_water_readings(
        self,
        station: Station,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Reading]:
        """Busca leituras de qualidade da água e converte os valores em objetos de domínio."""
        logger.info(
            "Iniciando ingestão de dados de água para estação %s no período %s a %s.",
            station.id,
            start_date,
            end_date,
        )
        try:
            import pandas as pd

            from src.ingestion.etl_water import consulta_api

            api_readings = consulta_api(
                lat=float(station.latitude),
                lng=float(station.longitude),
                from_date=start_date,
                to_date=end_date,
            )

            if "datetime" not in api_readings.columns:
                raise KeyError("A resposta da API não contém a coluna 'datetime'.")

            readings: list[Reading] = []

            for _, row in api_readings.iterrows():
                values = tuple(
                    ReadingValue(
                        parameter_code=column[len("pollutants_") : -len("_value")],
                        value=Decimal(str(row[column])),
                    )
                    for column in api_readings.columns
                    if column.startswith("pollutants_")
                    and column.endswith("_value")
                    if not pd.isna(row[column])
                )

                if values:
                    readings.append(
                        Reading(
                            station_id=station.id,
                            timestamp=pd.to_datetime(row["datetime"]).to_pydatetime(),
                            values=values,
                        )
                    )

            logger.info(
                "Ingestão de água concluída para estação %s: %d leitura(s) coletada(s).",
                station.id,
                len(readings),
            )
            return readings
        except Exception as e:
            tratar_erro(
                e,
                f"Falha na ingestão de dados de qualidade da água para estação {station.id}",
                encerrar=True,
            )
