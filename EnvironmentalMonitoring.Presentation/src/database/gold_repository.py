"""Repositório para atualização da camada Gold do data warehouse."""

import logging
import os
from datetime import datetime, date, timezone, timedelta
from uuid import UUID

try:
    import pyodbc
except ImportError:
    pyodbc = None

logger = logging.getLogger(__name__)


class GoldRepository:
    """Persistência e operações na camada Gold do SQL Server."""

    # Constante para cálculo de ReadingValueId
    READING_VALUE_ID_MULTIPLIER = 1000000

    def __init__(self, connection_string: str | None = None) -> None:
        """Inicializa repositório com string de conexão."""
        if connection_string:
            self.connection_string = connection_string
        else:
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
            
            server = os.getenv("SQL_SERVER")
            database = os.getenv("SQL_DATABASE")
            username = os.getenv("SQL_USERNAME")
            password = os.getenv("SQL_PASSWORD")
            
            if not all([server, database]):
                raise ValueError(
                    "Variáveis de ambiente necessárias não configuradas:\n"
                    "  SQL_SERVER\n  SQL_DATABASE"
                )
            
            if not all([username, password]):
                self.connection_string = (
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    "Trusted_Connection=yes;"
                    "TrustServerCertificate=yes;"
                )
            else:
                self.connection_string = (
                    "DRIVER={ODBC Driver 18 for SQL Server};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password};"
                    "Encrypt=yes;"
                    "TrustServerCertificate=no;"
                    "Connection Timeout=30;"
                )
        
        self.conn = None

    def _connect(self):
        """Estabelece conexão com banco de dados."""
        if pyodbc is None:
            raise ImportError("pyodbc não está instalado")
        try:
            self.conn = pyodbc.connect(self.connection_string)
        except Exception as e:
            raise Exception(f"Falha ao conectar ao banco: {e}")

    def _disconnect(self):
        """Encerra conexão com banco de dados."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def validate_gold_tables_exist(self) -> bool:
        """Valida que todas as tabelas Gold existem.
        
        IMPORTANTE: Usa a conexão existente, não abre/fecha a sua própria.
        """
        try:
            cursor = self.conn.cursor()
            
            tables = [
                "gold.DimStation",
                "gold.DimParameter",
                "gold.DimDate",
                "gold.DimTime",
                "gold.FactMeasurements"
            ]
            
            for table_name in tables:
                schema, table = table_name.split(".")
                cursor.execute(
                    """
                    SELECT 1 FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                    """,
                    schema,
                    table
                )
                if not cursor.fetchone():
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Erro ao validar tabelas Gold: {e}")
            return False

    def validate_dimensions_for_period(
        self,
        start_date: date,
        end_date: date
    ) -> tuple[bool, str]:
        """Valida que todas as dimensões necessárias existem para o período.
        
        IMPORTANTE: Usa a conexão existente, não abre/fecha a sua própria.
        
        Retorna:
            Tupla (sucesso, mensagem)
        """
        try:
            cursor = self.conn.cursor()
            
            # Converter para datetime exclusive do final
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            
            # Validar ParemeterId <= 999999
            cursor.execute(
                """
                SELECT MAX(p.Id)
                FROM dbo.Parameters p
                INNER JOIN dbo.ReadingValues rv ON p.Id = rv.ParameterId
                INNER JOIN dbo.Readings r ON rv.ReadingId = r.Id
                WHERE r.DateTime >= ? AND r.DateTime < ?
                """,
                start_dt,
                end_dt
            )
            row = cursor.fetchone()
            if row and row[0] and row[0] >= self.READING_VALUE_ID_MULTIPLIER:
                return False, (
                    f"ParameterId {row[0]} viola a regra de ReadingValueId "
                    f"(deve ser < {self.READING_VALUE_ID_MULTIPLIER})"
                )
            
            # Validar que todas as estações existem em DimStation
            cursor.execute(
                """
                SELECT DISTINCT rv.ParameterId
                FROM dbo.ReadingValues rv
                INNER JOIN dbo.Readings r ON rv.ReadingId = r.Id
                WHERE r.DateTime >= ? AND r.DateTime < ?
                AND NOT EXISTS (
                    SELECT 1 FROM gold.DimParameter dp
                    WHERE dp.ParameterId = rv.ParameterId
                )
                """,
                start_dt,
                end_dt
            )
            missing_params_rows = cursor.fetchall()
            if missing_params_rows:
                missing_ids = [str(row[0]) for row in missing_params_rows]
                return False, (
                    f"Os parâmetros {', '.join(missing_ids)} não existem em "
                    "gold.DimParameter. Popule a dimensão de parâmetros primeiro."
                )
            
            # Validar que todas as estações existem
            cursor.execute(
                """
                SELECT DISTINCT r.StationId
                FROM dbo.Readings r
                WHERE r.DateTime >= ? AND r.DateTime < ?
                AND NOT EXISTS (
                    SELECT 1 FROM gold.DimStation ds
                    WHERE ds.StationId = r.StationId
                )
                """,
                start_dt,
                end_dt
            )
            missing_stations_rows = cursor.fetchall()
            if missing_stations_rows:
                missing_ids = [str(row[0]) for row in missing_stations_rows]
                return False, (
                    f"As estações {', '.join(missing_ids)} não existem em "
                    "gold.DimStation. Popule a dimensão de estações primeiro."
                )
            
            return True, ""
        except Exception as e:
            logger.error(f"Erro ao validar dimensões: {e}")
            return False, f"Erro ao validar dimensões: {e}"

    def insert_dim_dates(self, start_date: date, end_date: date) -> int:
        """Insere datas ausentes em gold.DimDate para o período."""
        try:
            cursor = self.conn.cursor()
            
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            
            # Obter datas únicas das leituras que não existem em DimDate
            cursor.execute(
                """
                SELECT DISTINCT CAST(r.DateTime AS DATE) as ReadingDate
                FROM dbo.Readings r
                WHERE r.DateTime >= ? AND r.DateTime < ?
                AND NOT EXISTS (
                    SELECT 1 FROM gold.DimDate d
                    WHERE d.FullDate = CAST(r.DateTime AS DATE)
                )
                ORDER BY ReadingDate
                """,
                start_dt,
                end_dt
            )
            
            dates_to_insert = [row[0] for row in cursor.fetchall()]
            inserted_count = 0
            
            for reading_date in dates_to_insert:
                date_key = int(reading_date.strftime("%Y%m%d"))
                
                # Calcular atributos da data
                year = reading_date.year
                month = reading_date.month
                day = reading_date.day
                
                # Dia da semana (1=Segunda, 7=Domingo)
                weekday = reading_date.weekday()  # 0=Monday, 6=Sunday
                day_of_week = (weekday % 7) + 1
                
                # Semestre
                semester = 1 if month <= 6 else 2
                
                # Trimestre
                quarter = (month - 1) // 3 + 1
                
                # É fim de semana?
                is_weekend = 1 if day_of_week in [6, 7] else 0
                
                # É dia útil?
                is_business_day = 0 if day_of_week in [6, 7] else 1
                
                # Nomes em português
                month_names = [
                    "janeiro", "fevereiro", "março", "abril",
                    "maio", "junho", "julho", "agosto",
                    "setembro", "outubro", "novembro", "dezembro"
                ]
                day_names = [
                    "segunda-feira", "terça-feira", "quarta-feira",
                    "quinta-feira", "sexta-feira", "sábado", "domingo"
                ]
                
                month_name = month_names[month - 1]
                day_name = day_names[weekday]
                
                cursor.execute(
                    """
                    INSERT INTO gold.DimDate (
                        DateKey, FullDate, CalendarYear, CalendarSemester,
                        CalendarQuarter, MonthNumber, MonthName, DayOfMonth,
                        DayOfWeekNumber, DayOfWeekName, IsWeekend, IsBusinessDay
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    date_key, reading_date, year, semester, quarter,
                    month, month_name, day, day_of_week, day_name,
                    is_weekend, is_business_day
                )
                inserted_count += 1
            
            return inserted_count
        except Exception as e:
            logger.error(f"Erro ao inserir DimDate: {e}")
            raise

    def insert_dim_times(self, start_date: date, end_date: date) -> int:
        """Insere horários ausentes em gold.DimTime para o período."""
        try:
            cursor = self.conn.cursor()
            
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            
            # Obter horários únicos das leituras que não existem em DimTime
            cursor.execute(
                """
                SELECT DISTINCT CAST(r.DateTime AS TIME) as ReadingTime
                FROM dbo.Readings r
                WHERE r.DateTime >= ? AND r.DateTime < ?
                AND NOT EXISTS (
                    SELECT 1 FROM gold.DimTime t
                    WHERE t.FullTime = CAST(r.DateTime AS TIME)
                )
                ORDER BY ReadingTime
                """,
                start_dt,
                end_dt
            )
            
            times_to_insert = [row[0] for row in cursor.fetchall()]
            inserted_count = 0
            
            for reading_time in times_to_insert:
                # TimeKey format: HHMMSS
                hour = reading_time.hour
                minute = reading_time.minute
                second = reading_time.second
                
                time_key = hour * 10000 + minute * 100 + second
                
                cursor.execute(
                    """
                    INSERT INTO gold.DimTime (
                        TimeKey, FullTime, HourNumber, MinuteNumber, SecondNumber
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    time_key, reading_time, hour, minute, second
                )
                inserted_count += 1
            
            return inserted_count
        except Exception as e:
            logger.error(f"Erro ao inserir DimTime: {e}")
            raise

    def create_fact_analytics_temp_table(
        self,
        start_date: date,
        end_date: date,
        pipeline_run_id: UUID
    ) -> int:
        """Cria temp table com fatos e cálculos analíticos.
        
        Usa dados históricos para calcular Z-Score, IQR e média móvel,
        mas apenas insere/atualiza fatos do período selecionado.
        """
        try:
            cursor = self.conn.cursor()
            
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            
            # Criar temp table para armazenar fatos com cálculos
            cursor.execute("""
                DROP TABLE IF EXISTS #FactAnalytics
            """)
            
            # Query simplificada que evita window functions complexas
            # Usando abordagem mais direta e compatível com SQL Server
            # IMPORTANTE: Usar f-string para datas em SELECT INTO (pyodbc não parametriza bem neste cenário)
            query = f"""
            WITH AllReadings AS (
                SELECT
                    ds.StationKey,
                    dp.ParameterKey,
                    r.Id AS ReadingId,
                    (r.Id * {self.READING_VALUE_ID_MULTIPLIER} + rv.ParameterId) AS ReadingValueId,
                    r.DateTime AS MeasurementDateTime,
                    CAST(r.DateTime AS DATE) AS ReadingDate,
                    CAST(r.DateTime AS TIME) AS ReadingTime,
                    rv.Value AS MeasuredValue
                FROM dbo.ReadingValues rv
                INNER JOIN dbo.Readings r ON rv.ReadingId = r.Id
                LEFT JOIN gold.DimStation ds ON r.StationId = ds.StationId
                LEFT JOIN gold.DimParameter dp ON rv.ParameterId = dp.ParameterId
                WHERE ds.StationKey IS NOT NULL AND dp.ParameterKey IS NOT NULL
            ),
            WithDates AS (
                SELECT
                    *,
                    CAST(FORMAT(ReadingDate, 'yyyyMMdd') AS INT) AS DateKey,
                    (DATEPART(HOUR, MeasurementDateTime) * 10000 
                     + DATEPART(MINUTE, MeasurementDateTime) * 100
                     + DATEPART(SECOND, MeasurementDateTime)) AS TimeKey
                FROM AllReadings
            ),
            WithMovingAverage AS (
                SELECT
                    *,
                    AVG(MeasuredValue) OVER (
                        PARTITION BY StationKey, ParameterKey
                        ORDER BY MeasurementDateTime
                        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                    ) AS MovingAverageValue
                FROM WithDates
            ),
            StatisticsCalculated AS (
                SELECT DISTINCT
                    wd.StationKey,
                    wd.ParameterKey,
                    AVG(wd.MeasuredValue) OVER (PARTITION BY wd.StationKey, wd.ParameterKey) AS AvgValue,
                    STDEV(wd.MeasuredValue) OVER (PARTITION BY wd.StationKey, wd.ParameterKey) AS StdDev,
                    PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY wd.MeasuredValue) OVER (PARTITION BY wd.StationKey, wd.ParameterKey) AS Q1,
                    PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY wd.MeasuredValue) OVER (PARTITION BY wd.StationKey, wd.ParameterKey) AS Q3
                FROM WithDates wd
            ),
            WithOutliers AS (
                SELECT
                    wma.StationKey,
                    wma.ParameterKey,
                    wma.DateKey,
                    wma.TimeKey,
                    wma.ReadingId,
                    wma.ReadingValueId,
                    wma.MeasurementDateTime,
                    wma.MeasuredValue,
                    wma.MovingAverageValue,
                    CASE 
                        WHEN s.StdDev IS NULL OR s.StdDev = 0 THEN NULL
                        ELSE (wma.MeasuredValue - s.AvgValue) / s.StdDev
                    END AS ZScore,
                    ISNULL(s.Q1 - 1.5 * (s.Q3 - s.Q1), wma.MeasuredValue - 999999) AS IqrLowerBound,
                    ISNULL(s.Q3 + 1.5 * (s.Q3 - s.Q1), wma.MeasuredValue + 999999) AS IqrUpperBound
                FROM WithMovingAverage wma
                LEFT JOIN StatisticsCalculated s
                    ON wma.StationKey = s.StationKey
                    AND wma.ParameterKey = s.ParameterKey
            )
            SELECT
                StationKey,
                ParameterKey,
                DateKey,
                TimeKey,
                ReadingId,
                ReadingValueId,
                MeasurementDateTime,
                MeasuredValue,
                MovingAverageValue,
                ZScore,
                IqrLowerBound,
                IqrUpperBound,
                CASE
                    WHEN (MeasuredValue < IqrLowerBound OR MeasuredValue > IqrUpperBound)
                        AND ABS(ISNULL(ZScore, 0)) > 3 THEN 1
                    WHEN MeasuredValue < IqrLowerBound OR MeasuredValue > IqrUpperBound THEN 1
                    WHEN ABS(ISNULL(ZScore, 0)) > 3 THEN 1
                    ELSE 0
                END AS IsOutlier,
                CASE
                    WHEN (MeasuredValue < IqrLowerBound OR MeasuredValue > IqrUpperBound)
                        AND ABS(ISNULL(ZScore, 0)) > 3 THEN 'IQR+ZSCORE'
                    WHEN MeasuredValue < IqrLowerBound OR MeasuredValue > IqrUpperBound THEN 'IQR'
                    WHEN ABS(ISNULL(ZScore, 0)) > 3 THEN 'ZSCORE'
                    ELSE NULL
                END AS OutlierMethod,
                CAST('{pipeline_run_id}' AS UNIQUEIDENTIFIER) AS PipelineRunId
            INTO #FactAnalytics
            FROM WithOutliers
            WHERE MeasurementDateTime >= CAST('{start_dt.strftime('%Y-%m-%d')}' AS DATETIME) 
              AND MeasurementDateTime < CAST('{end_dt.strftime('%Y-%m-%d')}' AS DATETIME)
            """
            
            cursor.execute(query)
            
            # Retornar quantidade de registros inseridos
            cursor.execute("SELECT COUNT(*) FROM #FactAnalytics")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Erro ao criar temp table de analytics: {e}")
            raise

    def upsert_facts(self) -> tuple[int, int]:
        """Realiza UPSERT dos fatos da temp table.
        
        Retorna:
            Tupla (inseridos, atualizados)
        """
        try:
            cursor = self.conn.cursor()
            
            # Atualizar fatos existentes
            cursor.execute("""
                UPDATE fm
                SET
                    fm.StationKey = fa.StationKey,
                    fm.ParameterKey = fa.ParameterKey,
                    fm.DateKey = fa.DateKey,
                    fm.TimeKey = fa.TimeKey,
                    fm.ReadingId = fa.ReadingId,
                    fm.MeasurementDateTime = fa.MeasurementDateTime,
                    fm.MeasuredValue = fa.MeasuredValue,
                    fm.MovingAverageValue = fa.MovingAverageValue,
                    fm.ZScore = fa.ZScore,
                    fm.IqrLowerBound = fa.IqrLowerBound,
                    fm.IqrUpperBound = fa.IqrUpperBound,
                    fm.IsOutlier = fa.IsOutlier,
                    fm.OutlierMethod = fa.OutlierMethod,
                    fm.LoadedAt = SYSUTCDATETIME(),
                    fm.PipelineRunId = fa.PipelineRunId
                FROM gold.FactMeasurements fm
                INNER JOIN #FactAnalytics fa
                    ON fm.ReadingValueId = fa.ReadingValueId
                WHERE fm.ReadingValueId = fa.ReadingValueId
            """)
            
            updated_count = cursor.rowcount
            
            # Inserir fatos novos
            cursor.execute("""
                INSERT INTO gold.FactMeasurements (
                    StationKey, ParameterKey, DateKey, TimeKey,
                    ReadingId, ReadingValueId, MeasurementDateTime,
                    MeasuredValue, MovingAverageValue, ZScore,
                    IqrLowerBound, IqrUpperBound, IsOutlier,
                    OutlierMethod, LoadedAt, PipelineRunId
                )
                SELECT
                    fa.StationKey, fa.ParameterKey, fa.DateKey, fa.TimeKey,
                    fa.ReadingId, fa.ReadingValueId, fa.MeasurementDateTime,
                    fa.MeasuredValue, fa.MovingAverageValue, fa.ZScore,
                    fa.IqrLowerBound, fa.IqrUpperBound, fa.IsOutlier,
                    fa.OutlierMethod, SYSUTCDATETIME(), fa.PipelineRunId
                FROM #FactAnalytics fa
                WHERE NOT EXISTS (
                    SELECT 1 FROM gold.FactMeasurements fm
                    WHERE fm.ReadingValueId = fa.ReadingValueId
                )
            """)
            
            inserted_count = cursor.rowcount
            
            return inserted_count, updated_count
        except Exception as e:
            logger.error(f"Erro ao fazer UPSERT de fatos: {e}")
            raise

    def get_available_date_range(self) -> tuple[date, date] | tuple[None, None]:
        """Obtém a faixa de datas disponíveis na camada Silver (dbo.Readings).
        
        Retorna:
            Tupla (min_date, max_date) ou (None, None) se não houver dados
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    CAST(MIN(DateTime) AS DATE) as MinDate,
                    CAST(MAX(DateTime) AS DATE) as MaxDate
                FROM dbo.Readings
                WHERE DateTime IS NOT NULL
            """)
            
            row = cursor.fetchone()
            if row and row[0] is not None and row[1] is not None:
                return row[0], row[1]
            else:
                return None, None
        except Exception as e:
            logger.error(f"Erro ao buscar faixa de datas disponíveis: {e}")
            return None, None

    def cleanup_temp_table(self):
        """Remove a temp table de analytics."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS #FactAnalytics")
        except Exception as e:
            logger.error(f"Erro ao limpar temp table: {e}")
            raise
