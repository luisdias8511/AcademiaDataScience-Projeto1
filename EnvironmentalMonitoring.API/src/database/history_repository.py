"""Repositório simples para consultas históricas no SQL Server."""

from contextlib import closing
from datetime import datetime
from decimal import Decimal
from decimal import ROUND_HALF_UP

import pyodbc

from src.database.connection import get_connection
from src.exceptions import DatabaseQueryError
from src.models.database_models import ParameterValueRecord, ReadingRecord, Station, StationRecord


class HistoryRepository:
    """Executa consultas de leitura no banco com SQL parametrizado."""

    def get_top_stations(self, limit: int = 10) -> list[Station]:
        """Retorna as primeiras estações ordenadas por identificador."""
        if limit <= 0:
            raise ValueError("O limite de estações deve ser maior que zero.")

        query = """
            SELECT TOP (?) Id, Code, Name, Latitude, Longitude
            FROM Stations
            ORDER BY Id
        """

        stations: list[Station] = []
        with closing(get_connection()) as connection:
            cursor = connection.cursor()
            cursor.execute(query, limit)
            rows = cursor.fetchall()

            for row in rows:
                stations.append(
                    Station(
                        id=int(row.Id),
                        code=str(row.Code),
                        name=str(row.Name),
                        latitude=Decimal(str(row.Latitude)),
                        longitude=Decimal(str(row.Longitude)),
                    )
                )

        return stations

    def get_station_by_coordinates(
        self,
        latitude: Decimal,
        longitude: Decimal,
    ) -> StationRecord | None:
        """Retorna estação por coordenadas exatas com arredondamento de 6 casas."""
        lat_rounded = self._round_coordinate(latitude)
        lng_rounded = self._round_coordinate(longitude)

        query = """
            SELECT TOP (1) Id, Code, Name, Latitude, Longitude
            FROM Stations
            WHERE Latitude = ? AND Longitude = ?
        """

        try:
            with closing(get_connection()) as connection:
                cursor = connection.cursor()
                cursor.execute(query, lat_rounded, lng_rounded)
                row = cursor.fetchone()

                if row is None:
                    return None

                return StationRecord(
                    id=int(row.Id),
                    code=str(row.Code),
                    name=str(row.Name),
                    latitude=Decimal(str(row.Latitude)),
                    longitude=Decimal(str(row.Longitude)),
                )
        except pyodbc.Error as exc:
            raise DatabaseQueryError("Falha ao consultar a estação.") from exc

    def get_history(
        self,
        station_id: int,
        category_code: str,
        start_date: datetime,
        end_date: datetime,
        page: int,
        page_size: int,
    ) -> tuple[list[ReadingRecord], int]:
        """Retorna leituras históricas paginadas e total de leituras distintas."""
        try:
            total_elements = self._count_distinct_readings(
                station_id=station_id,
                category_code=category_code,
                start_date=start_date,
                end_date=end_date,
            )

            if total_elements == 0:
                return [], 0

            offset = page * page_size
            readings = self._fetch_paged_readings(
                station_id=station_id,
                category_code=category_code,
                start_date=start_date,
                end_date=end_date,
                offset=offset,
                page_size=page_size,
            )
        except pyodbc.Error as exc:
            raise DatabaseQueryError("Falha ao consultar o histórico.") from exc

        return readings, total_elements

    @staticmethod
    def _round_coordinate(value: Decimal) -> Decimal:
        """Arredonda coordenada para 6 casas decimais."""
        return value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    def _count_distinct_readings(
        self,
        station_id: int,
        category_code: str,
        start_date: datetime,
        end_date: datetime,
    ) -> int:
        """Conta leituras distintas por estação, categoria e intervalo."""
        query = """
            SELECT COUNT(DISTINCT r.Id) AS TotalElements
            FROM Readings r
            INNER JOIN ReadingValues rv ON rv.ReadingId = r.Id
            INNER JOIN Parameters p ON p.Id = rv.ParameterId
            INNER JOIN ParameterCategories pc ON pc.Id = p.CategoryId
            WHERE r.StationId = ?
              AND pc.Code = ?
              AND r.DateTime >= ?
              AND r.DateTime < ?
        """

        with closing(get_connection()) as connection:
            cursor = connection.cursor()
            cursor.execute(
                query,
                station_id,
                category_code,
                start_date,
                end_date,
            )
            row = cursor.fetchone()
            return int(row.TotalElements if row and row.TotalElements is not None else 0)

    def _fetch_paged_readings(
        self,
        station_id: int,
        category_code: str,
        start_date: datetime,
        end_date: datetime,
        offset: int,
        page_size: int,
    ) -> list[ReadingRecord]:
        """Busca leituras paginadas mantendo paginação no SQL via OFFSET/FETCH."""
        query = """
            WITH FilteredReadings AS (
                SELECT DISTINCT r.Id, r.DateTime
                FROM Readings r
                INNER JOIN ReadingValues rv ON rv.ReadingId = r.Id
                INNER JOIN Parameters p ON p.Id = rv.ParameterId
                INNER JOIN ParameterCategories pc ON pc.Id = p.CategoryId
                WHERE r.StationId = ?
                  AND pc.Code = ?
                  AND r.DateTime >= ?
                  AND r.DateTime < ?
            ),
            PagedReadings AS (
                SELECT fr.Id, fr.DateTime
                FROM FilteredReadings fr
                ORDER BY fr.DateTime, fr.Id
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            )
            SELECT
                pr.Id AS ReadingId,
                pr.DateTime AS ReadingDateTime,
                p.CodeApi AS ParameterCodeApi,
                p.Name AS ParameterName,
                p.Unit AS ParameterUnit,
                rv.Value AS ReadingValue
            FROM PagedReadings pr
            INNER JOIN ReadingValues rv ON rv.ReadingId = pr.Id
            INNER JOIN Parameters p ON p.Id = rv.ParameterId
            INNER JOIN ParameterCategories pc ON pc.Id = p.CategoryId
            WHERE pc.Code = ?
            ORDER BY pr.DateTime, pr.Id, p.Id
        """

        with closing(get_connection()) as connection:
            cursor = connection.cursor()
            cursor.execute(
                query,
                station_id,
                category_code,
                start_date,
                end_date,
                offset,
                page_size,
                category_code,
            )
            rows = cursor.fetchall()

        if not rows:
            return []

        grouped: dict[int, dict[str, object]] = {}
        ordered_ids: list[int] = []

        for row in rows:
            reading_id = int(row.ReadingId)
            if reading_id not in grouped:
                grouped[reading_id] = {
                    "timestamp": row.ReadingDateTime,
                    "values": [],
                }
                ordered_ids.append(reading_id)

            values = grouped[reading_id]["values"]
            assert isinstance(values, list)
            values.append(
                ParameterValueRecord(
                    code_api=str(row.ParameterCodeApi),
                    name=str(row.ParameterName),
                    unit=str(row.ParameterUnit) if row.ParameterUnit is not None else None,
                    value=Decimal(str(row.ReadingValue)),
                )
            )

        readings: list[ReadingRecord] = []
        for reading_id in ordered_ids:
            item = grouped[reading_id]
            timestamp = item["timestamp"]
            values = item["values"]
            assert isinstance(values, list)
            readings.append(
                ReadingRecord(
                    id=reading_id,
                    timestamp=timestamp,
                    values=tuple(values),
                )
            )

        return readings

