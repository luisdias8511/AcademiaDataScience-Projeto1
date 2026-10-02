"""Serviço de ingestion na base de dados."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import numpy as np
import pandas as pd

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

            # Pré-filtrar colunas de parâmetros UMA VEZ (não a cada linha)
            param_columns = [
                col for col in api_readings.columns
                if col.startswith("parameters_") and col.endswith("_value")
            ]

            # Converter para numpy (muito mais rápido que iterrows)
            data_array = api_readings[param_columns].values
            # Manter como pandas Series com timezone para evitar problemas de conversão
            datetime_series = pd.to_datetime(api_readings["datetime"], utc=True)

            readings: list[Reading] = []

            # Iterar sobre numpy (2-3x mais rápido)
            for i in range(len(data_array)):
                row_data = data_array[i]

                # Usar numpy.isnan() vetorizado
                try:
                    row_float = row_data.astype(float)
                except (ValueError, TypeError):
                    row_float = np.array([float(x) if pd.notna(x) else np.nan for x in row_data])
                
                valid_mask = ~np.isnan(row_float)

                if valid_mask.any():
                    values = tuple(
                        ReadingValue(
                            parameter_code=param_columns[j][len("parameters_") : -len("_value")],
                            value=Decimal(str(row_data[j])),
                        )
                        for j in np.where(valid_mask)[0]
                    )

                    readings.append(
                        Reading(
                            station_id=station.id,
                            timestamp=datetime_series.iloc[i].to_pydatetime(),
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

            # OTIMIZAÇÃO 1: Pré-filtrar colunas de poluentes UMA VEZ (não a cada linha)
            pollutant_columns = [
                col for col in api_readings.columns
                if col.startswith("pollutants_") and col.endswith("_value")
            ]

            # OTIMIZAÇÃO 2: Converter para numpy (muito mais rápido que iterrows)
            data_array = api_readings[pollutant_columns].values
            # Manter como pandas Series com timezone para evitar problemas de conversão
            datetime_series = pd.to_datetime(api_readings["datetime"], utc=True)

            readings: list[Reading] = []

            # OTIMIZAÇÃO 3: Iterar sobre numpy (2-3x mais rápido)
            for i in range(len(data_array)):
                row_data = data_array[i]

                # OTIMIZAÇÃO 4: Usar numpy.isnan() vetorizado
                try:
                    row_float = row_data.astype(float)
                except (ValueError, TypeError):
                    row_float = np.array([float(x) if pd.notna(x) else np.nan for x in row_data])
                
                valid_mask = ~np.isnan(row_float)

                if valid_mask.any():
                    values = tuple(
                        ReadingValue(
                            parameter_code=pollutant_columns[j][len("pollutants_") : -len("_value")],
                            value=Decimal(str(row_data[j])),
                        )
                        for j in np.where(valid_mask)[0]
                    )

                    readings.append(
                        Reading(
                            station_id=station.id,
                            timestamp=datetime_series.iloc[i].to_pydatetime(),
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
