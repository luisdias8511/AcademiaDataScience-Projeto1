"""Repositório unificado de leituras ambientais."""

import logging
import os
from collections.abc import Sequence
from datetime import datetime, timezone
from decimal import Decimal

from src.models.reading import Reading
from src.models.station import Station
from src.models.parameter import Parameter

logger = logging.getLogger(__name__)


class ReadingRepository:
    """Persistência e recuperação de leituras do SQL Server."""

    def __init__(self, connection_string: str | None = None) -> None:
        """Inicializa repositório com string de conexão.
        
        Args:
            connection_string: String de conexão customizada (opcional).
                              Se não fornecida, carrega automaticamente de variáveis de ambiente.
        
        Raises:
            ValueError: Se variáveis de ambiente necessárias não forem configuradas.
        """
        if connection_string:
            # Usar string customizada fornecida
            self.connection_string = connection_string
        else:
            # Carregar variáveis de ambiente e construir string
            # Tenta carregar do .env se disponível
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                # Se dotenv não estiver disponível, prossegue com variáveis do sistema
                pass
            
            # Obter variáveis de ambiente
            server = os.getenv("SQL_SERVER")
            database = os.getenv("SQL_DATABASE")
            
            if not all([server, database]):
                raise ValueError(
                    "Variáveis de ambiente necessárias não configuradas:\n"
                    "  SQL_SERVER (ex: localhost\\SQLEXPRESS)\n"
                    "  SQL_DATABASE (ex: EnvironmentalMonitoring)\n"
                    "\nConfigure no arquivo .env ou nas variáveis de ambiente do sistema."
                )
            
            # Construir string de conexão com Windows Authentication
            self.connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
        
        self.conn = None

    def _connect(self):
        """Estabelece conexão com banco de dados."""
        try:
            import pyodbc
            self.conn = pyodbc.connect(self.connection_string)
        except Exception as e:
            raise Exception(f"Falha ao conectar ao banco: {e}")

    def _disconnect(self):
        """Encerra conexão com banco de dados."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_station_by_id(self, station_id: int) -> Station | None:
        """Busca estação pelo ID."""
        try:
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT Id, Code, Name, Latitude, Longitude FROM Stations WHERE Id = ?",
                station_id,
            )
            row = cursor.fetchone()
            self._disconnect()

            if row:
                return Station(
                    id=row[0],
                    code=row[1],
                    name=row[2],
                    latitude=Decimal(str(row[3])),
                    longitude=Decimal(str(row[4])),
                )
            return None
        except Exception as e:
            raise Exception(f"Erro ao buscar estação: {e}")

    def _get_parameter_id_by_code(self, cursor, parameter_code: str) -> int | None:
        """Busca ID do parâmetro pelo código usando cursor existente."""
        try:
            cursor.execute(
                "SELECT Id FROM Parameters WHERE Code = ?",
                parameter_code,
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            raise Exception(f"Erro ao buscar parâmetro: {e}")

    def get_parameter_id_by_code(self, parameter_code: str) -> int | None:
        """Busca ID do parâmetro pelo código (para uso externo)."""
        try:
            self._connect()
            cursor = self.conn.cursor()
            param_id = self._get_parameter_id_by_code(cursor, parameter_code)
            self._disconnect()
            return param_id
        except Exception as e:
            raise Exception(f"Erro ao buscar parâmetro: {e}")

    def save(self, reading: Reading) -> int:
        """Persiste uma leitura no banco com transação."""
        try:
            self._connect()
            cursor = self.conn.cursor()

            # Converte timestamp para UTC sem timezone e sem microssegundos
            database_timestamp = (
                reading.timestamp
                .astimezone(timezone.utc)
                .replace(tzinfo=None, microsecond=0)
            )

            logger.info(
                "Persistindo leitura da estação %s.",
                reading.station_id,
            )

            # Insere na tabela Readings com OUTPUT para obter o ID
            cursor.execute(
                """
                INSERT INTO Readings (StationId, DateTime)
                OUTPUT INSERTED.Id
                VALUES (?, ?)
                """,
                reading.station_id,
                database_timestamp,
            )
            reading_id = cursor.fetchone()[0]
            logger.debug(
                "Leitura %s criada.",
                reading_id,
            )

            # Insere valores na tabela ReadingValues
            for value in reading.values:
                param_id = self._get_parameter_id_by_code(cursor, value.parameter_code)
                if not param_id:
                    self.conn.rollback()
                    self._disconnect()
                    raise Exception(
                        f"Parâmetro não encontrado: {value.parameter_code}"
                    )

                cursor.execute(
                    """
                    INSERT INTO ReadingValues (ReadingId, ParameterId, Value)
                    VALUES (?, ?, ?)
                    """,
                    reading_id,
                    param_id,
                    float(value.value),
                )
                logger.debug(
                    "Valor do parâmetro %s persistido.",
                    value.parameter_code,
                )

            # Commit da transação
            self.conn.commit()
            logger.info(
                "Leitura %s persistida com sucesso.",
                reading_id,
            )
            self._disconnect()
            return reading_id

        except Exception as e:
            if self.conn:
                try:
                    self.conn.rollback()
                    logger.warning("Transação revertida devido a erro.")
                except Exception:
                    pass
            self._disconnect()
            raise Exception(f"Erro ao persistir leitura: {e}")

    def save_many(self, readings: Sequence[Reading]) -> list[int]:
        """Persiste múltiplas leituras no banco."""
        reading_ids: list[int] = []
        for reading in readings:
            reading_id = self.save(reading)
            reading_ids.append(reading_id)
        return reading_ids

    def get_parameter_values(
        self,
        parameter_code: str,
        start_date: datetime,
        end_date: datetime,
        station_id: int | None = None,
    ) -> list[float]:
        """Busca valores de um parâmetro em um período."""
        try:
            self._connect()
            cursor = self.conn.cursor()

            param_id = self._get_parameter_id_by_code(cursor, parameter_code)
            if not param_id:
                self._disconnect()
                return []

            logger.debug(
                "Buscando valores do parâmetro %s de %s até %s.",
                parameter_code,
                start_date,
                end_date,
            )

            if station_id:
                cursor.execute(
                    """
                    SELECT rv.Value
                    FROM ReadingValues rv
                    INNER JOIN Readings r ON rv.ReadingId = r.Id
                    INNER JOIN Parameters p ON rv.ParameterId = p.Id
                    WHERE p.Code = ?
                      AND r.DateTime BETWEEN ? AND ?
                      AND r.StationId = ?
                    """,
                    parameter_code,
                    start_date,
                    end_date,
                    station_id,
                )
            else:
                cursor.execute(
                    """
                    SELECT rv.Value
                    FROM ReadingValues rv
                    INNER JOIN Readings r ON rv.ReadingId = r.Id
                    INNER JOIN Parameters p ON rv.ParameterId = p.Id
                    WHERE p.Code = ?
                      AND r.DateTime BETWEEN ? AND ?
                    """,
                    parameter_code,
                    start_date,
                    end_date,
                )

            rows = cursor.fetchall()
            self._disconnect()
            return [float(row[0]) for row in rows]
        except Exception as e:
            self._disconnect()
            raise Exception(f"Erro ao buscar valores de parâmetro: {e}")

    def get_by_station(
        self,
        station_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Reading]:
        """Busca leituras de uma estação em um período."""
        try:
            self._connect()
            cursor = self.conn.cursor()

            logger.debug(
                "Buscando leituras da estação %s de %s até %s.",
                station_id,
                start_date,
                end_date,
            )

            cursor.execute(
                """
                SELECT r.Id, r.StationId, r.DateTime
                FROM Readings r
                WHERE r.StationId = ?
                  AND r.DateTime BETWEEN ? AND ?
                ORDER BY r.DateTime
                """,
                station_id,
                start_date,
                end_date,
            )

            rows = cursor.fetchall()
            readings: list[Reading] = []

            for row in rows:
                reading_id = row[0]
                # Busca valores da leitura com unidade do Parameters
                cursor.execute(
                    """
                    SELECT p.Code, rv.Value, p.Unit
                    FROM ReadingValues rv
                    INNER JOIN Parameters p ON rv.ParameterId = p.Id
                    WHERE rv.ReadingId = ?
                    """,
                    reading_id,
                )

                from src.models.reading_value import ReadingValue
                values = [
                    ReadingValue(
                        parameter_code=v[0],
                        value=Decimal(str(v[1])),
                        unit=v[2],
                    )
                    for v in cursor.fetchall()
                ]

                if values:
                    # Restaura timezone UTC ao ler do banco
                    reading_datetime = row[2].replace(tzinfo=timezone.utc)
                    reading = Reading(
                        station_id=row[1],
                        timestamp=reading_datetime,
                        values=tuple(values),
                    )
                    readings.append(reading)
                    logger.debug(
                        "Leitura %s recuperada com %d valor(es).",
                        reading_id,
                        len(values),
                    )

            logger.info(
                "%d leitura(s) recuperada(s) para a estação %s.",
                len(readings),
                station_id,
            )
            self._disconnect()
            return readings
        except Exception as e:
            self._disconnect()
            raise Exception(f"Erro ao buscar leituras: {e}")

    def get_stations(self) -> list[Station]:
        """Busca todas as estações cadastradas."""
        try:
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT Id, Code, Name, Latitude, Longitude FROM Stations ORDER BY Code"
            )
            rows = cursor.fetchall()
            self._disconnect()

            stations = [
                Station(
                    id=row[0],
                    code=row[1],
                    name=row[2],
                    latitude=Decimal(str(row[3])),
                    longitude=Decimal(str(row[4])),
                )
                for row in rows
            ]
            return stations
        except Exception as e:
            raise Exception(f"Erro ao buscar estações: {e}")

    def get_parameter_by_code(self, parameter_code: str) -> Parameter | None:
        """Busca parâmetro pelo código e retorna objeto Parameter."""
        try:
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT Id, Code, Name, Unit FROM Parameters WHERE Code = ?",
                parameter_code,
            )
            row = cursor.fetchone()
            self._disconnect()

            if row:
                return Parameter(
                    id=row[0],
                    code=row[1],
                    name=row[2],
                    unit=row[3],
                )
            return None
        except Exception as e:
            raise Exception(f"Erro ao buscar parâmetro: {e}")

    def get_weather_parameters(self) -> list[Parameter]:
        """Busca todos os parâmetros meteorológicos cadastrados."""
        try:
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT Id, Code, Name, Unit FROM Parameters ORDER BY Code"
            )
            rows = cursor.fetchall()
            self._disconnect()

            parameters = [
                Parameter(
                    id=row[0],
                    code=row[1],
                    name=row[2],
                    unit=row[3],
                )
                for row in rows
            ]
            return parameters
        except Exception as e:
            raise Exception(f"Erro ao buscar parâmetros: {e}")

    def get_weather_parameters_codes(self) -> list[str]:
        """Busca os códigos de todos os parâmetros meteorológicos cadastrados."""
        try:
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT Code FROM Parameters ORDER BY Code"
            )
            rows = cursor.fetchall()
            self._disconnect()

            codes = [row[0] for row in rows]
            return codes
        except Exception as e:
            raise Exception(f"Erro ao buscar códigos de parâmetros: {e}")
