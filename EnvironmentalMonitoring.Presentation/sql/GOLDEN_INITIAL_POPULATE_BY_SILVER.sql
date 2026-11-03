USE EnvironmentalMonitoring;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRANSACTION;

    /* ============================================================
       1. VALIDAÇÕES
       ============================================================ */

    IF OBJECT_ID('gold.DimStation', 'U') IS NULL
        THROW 50001, 'A tabela gold.DimStation não existe.', 1;

    IF OBJECT_ID('gold.DimParameter', 'U') IS NULL
        THROW 50002, 'A tabela gold.DimParameter não existe.', 1;

    IF OBJECT_ID('gold.DimDate', 'U') IS NULL
        THROW 50003, 'A tabela gold.DimDate não existe.', 1;

    IF OBJECT_ID('gold.DimTime', 'U') IS NULL
        THROW 50004, 'A tabela gold.DimTime não existe.', 1;

    IF OBJECT_ID('gold.FactMeasurements', 'U') IS NULL
        THROW 50005, 'A tabela gold.FactMeasurements não existe.', 1;

    /*
       Como dbo.ReadingValues possui chave composta e não possui Id,
       ReadingValueId será calculado por:

       ReadingId * 1.000.000 + ParameterId
    */

    IF EXISTS
    (
        SELECT 1
        FROM dbo.ReadingValues
        WHERE ParameterId >= 1000000
    )
    BEGIN
        THROW 50006,
              'ParameterId maior ou igual a 1.000.000. Não foi possível gerar ReadingValueId.',
              1;
    END;

    /* ============================================================
       2. POPULAR DIMDATE COM AS DATAS DA SILVER
       ============================================================ */

    ;WITH SourceDates AS
    (
        SELECT DISTINCT
            CAST(r.DateTime AS DATE) AS FullDate
        FROM dbo.Readings r
    ),
    DateData AS
    (
        SELECT
            sd.FullDate,

            CONVERT
            (
                INT,
                CONVERT(CHAR(8), sd.FullDate, 112)
            ) AS DateKey,

            YEAR(sd.FullDate) AS CalendarYear,

            CASE
                WHEN MONTH(sd.FullDate) <= 6 THEN 1
                ELSE 2
            END AS CalendarSemester,

            DATEPART(QUARTER, sd.FullDate) AS CalendarQuarter,
            MONTH(sd.FullDate) AS MonthNumber,

            CHOOSE
            (
                MONTH(sd.FullDate),
                'Janeiro',
                'Fevereiro',
                'Março',
                'Abril',
                'Maio',
                'Junho',
                'Julho',
                'Agosto',
                'Setembro',
                'Outubro',
                'Novembro',
                'Dezembro'
            ) AS MonthName,

            DAY(sd.FullDate) AS DayOfMonth,

            (
                DATEDIFF
                (
                    DAY,
                    CONVERT(DATE, '19000101', 112),
                    sd.FullDate
                ) % 7
            ) + 1 AS DayOfWeekNumber

        FROM SourceDates sd
    )
    INSERT INTO gold.DimDate
    (
        DateKey,
        FullDate,
        CalendarYear,
        CalendarSemester,
        CalendarQuarter,
        MonthNumber,
        MonthName,
        DayOfMonth,
        DayOfWeekNumber,
        DayOfWeekName,
        IsWeekend,
        IsBusinessDay
    )
    SELECT
        d.DateKey,
        d.FullDate,
        d.CalendarYear,
        d.CalendarSemester,
        d.CalendarQuarter,
        d.MonthNumber,
        d.MonthName,
        d.DayOfMonth,
        d.DayOfWeekNumber,

        CHOOSE
        (
            d.DayOfWeekNumber,
            'Segunda-feira',
            'Terça-feira',
            'Quarta-feira',
            'Quinta-feira',
            'Sexta-feira',
            'Sábado',
            'Domingo'
        ),

        CASE
            WHEN d.DayOfWeekNumber IN (6, 7) THEN 1
            ELSE 0
        END,

        CASE
            WHEN d.DayOfWeekNumber IN (6, 7) THEN 0
            ELSE 1
        END

    FROM DateData d

    WHERE NOT EXISTS
    (
        SELECT 1
        FROM gold.DimDate dd
        WHERE dd.FullDate = d.FullDate
    );

    DECLARE @InsertedDates INT = @@ROWCOUNT;

    /* ============================================================
       3. POPULAR DIMTIME COM OS HORÁRIOS DA SILVER
       ============================================================ */

    ;WITH SourceTimes AS
    (
        SELECT DISTINCT
            CAST(r.DateTime AS TIME(0)) AS FullTime
        FROM dbo.Readings r
    ),
    TimeData AS
    (
        SELECT
            st.FullTime,

            DATEPART(HOUR, st.FullTime) * 10000
            + DATEPART(MINUTE, st.FullTime) * 100
            + DATEPART(SECOND, st.FullTime) AS TimeKey,

            DATEPART(HOUR, st.FullTime) AS HourNumber,
            DATEPART(MINUTE, st.FullTime) AS MinuteNumber,
            DATEPART(SECOND, st.FullTime) AS SecondNumber

        FROM SourceTimes st
    )
    INSERT INTO gold.DimTime
    (
        TimeKey,
        FullTime,
        HourNumber,
        MinuteNumber,
        SecondNumber
    )
    SELECT
        t.TimeKey,
        t.FullTime,
        t.HourNumber,
        t.MinuteNumber,
        t.SecondNumber

    FROM TimeData t

    WHERE NOT EXISTS
    (
        SELECT 1
        FROM gold.DimTime dt
        WHERE dt.FullTime = t.FullTime
    );

    DECLARE @InsertedTimes INT = @@ROWCOUNT;

    /* ============================================================
       4. VALIDAR DIMENSÕES
       ============================================================ */

    IF EXISTS
    (
        SELECT 1
        FROM dbo.Readings r

        LEFT JOIN gold.DimStation ds
            ON ds.StationId = r.StationId

        WHERE ds.StationKey IS NULL
    )
    BEGIN
        THROW 50007,
              'Existem estações da Silver que ainda não foram carregadas em gold.DimStation.',
              1;
    END;

    IF EXISTS
    (
        SELECT 1
        FROM dbo.ReadingValues rv

        LEFT JOIN gold.DimParameter dp
            ON dp.ParameterId = rv.ParameterId

        WHERE dp.ParameterKey IS NULL
    )
    BEGIN
        THROW 50008,
              'Existem parâmetros da Silver que ainda não foram carregados em gold.DimParameter.',
              1;
    END;

    /* ============================================================
       5. PREPARAR BASE ANALÍTICA

       Uma linha por:
       estação + parâmetro + leitura
       ============================================================ */

    IF OBJECT_ID('tempdb..#FactAnalytics') IS NOT NULL
        DROP TABLE #FactAnalytics;

    ;WITH BaseMeasurements AS
    (
        SELECT
            ds.StationKey,
            dp.ParameterKey,
            dd.DateKey,
            dt.TimeKey,

            r.Id AS ReadingId,

            (
                rv.ReadingId * CAST(1000000 AS BIGINT)
            ) + rv.ParameterId AS ReadingValueId,

            r.DateTime AS MeasurementDateTime,
            CAST(rv.Value AS DECIMAL(18,4)) AS MeasuredValue,

            AVG(CAST(rv.Value AS DECIMAL(38,10))) OVER
            (
                PARTITION BY
                    r.StationId,
                    rv.ParameterId

                ORDER BY
                    r.DateTime,
                    r.Id

                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) AS MovingAverageValue,

            AVG(CAST(rv.Value AS DECIMAL(38,10))) OVER
            (
                PARTITION BY
                    r.StationId,
                    rv.ParameterId
            ) AS GroupAverage,

            STDEV(CAST(rv.Value AS FLOAT)) OVER
            (
                PARTITION BY
                    r.StationId,
                    rv.ParameterId
            ) AS GroupStandardDeviation,

            PERCENTILE_CONT(0.25) WITHIN GROUP
            (
                ORDER BY CAST(rv.Value AS FLOAT)
            ) OVER
            (
                PARTITION BY
                    r.StationId,
                    rv.ParameterId
            ) AS Q1,

            PERCENTILE_CONT(0.75) WITHIN GROUP
            (
                ORDER BY CAST(rv.Value AS FLOAT)
            ) OVER
            (
                PARTITION BY
                    r.StationId,
                    rv.ParameterId
            ) AS Q3

        FROM dbo.ReadingValues rv

        INNER JOIN dbo.Readings r
            ON r.Id = rv.ReadingId

        INNER JOIN gold.DimStation ds
            ON ds.StationId = r.StationId

        INNER JOIN gold.DimParameter dp
            ON dp.ParameterId = rv.ParameterId

        INNER JOIN gold.DimDate dd
            ON dd.FullDate = CAST(r.DateTime AS DATE)

        INNER JOIN gold.DimTime dt
            ON dt.FullTime = CAST(r.DateTime AS TIME(0))
    ),
    CalculatedStatistics AS
    (
        SELECT
            bm.*,

            CASE
                WHEN bm.GroupStandardDeviation IS NULL
                     OR bm.GroupStandardDeviation = 0
                    THEN NULL
                ELSE
                    (
                        CAST(bm.MeasuredValue AS FLOAT)
                        - CAST(bm.GroupAverage AS FLOAT)
                    )
                    / bm.GroupStandardDeviation
            END AS CalculatedZScore,

            bm.Q3 - bm.Q1 AS IqrValue,

            bm.Q1 - 1.5 * (bm.Q3 - bm.Q1)
                AS CalculatedIqrLowerBound,

            bm.Q3 + 1.5 * (bm.Q3 - bm.Q1)
                AS CalculatedIqrUpperBound

        FROM BaseMeasurements bm
    ),
    OutlierClassification AS
    (
        SELECT
            cs.*,

            CASE
                WHEN cs.MeasuredValue < cs.CalculatedIqrLowerBound
                  OR cs.MeasuredValue > cs.CalculatedIqrUpperBound
                    THEN 1
                ELSE 0
            END AS IsIqrOutlier,

            CASE
                WHEN ABS(cs.CalculatedZScore) > 3
                    THEN 1
                ELSE 0
            END AS IsZScoreOutlier

        FROM CalculatedStatistics cs
    )
    SELECT
        oc.StationKey,
        oc.ParameterKey,
        oc.DateKey,
        oc.TimeKey,

        oc.ReadingId,
        oc.ReadingValueId,
        oc.MeasurementDateTime,
        oc.MeasuredValue,

        CAST
        (
            oc.MovingAverageValue
            AS DECIMAL(18,4)
        ) AS MovingAverageValue,

        CAST
        (
            oc.CalculatedZScore
            AS DECIMAL(18,6)
        ) AS ZScore,

        CAST
        (
            oc.CalculatedIqrLowerBound
            AS DECIMAL(18,4)
        ) AS IqrLowerBound,

        CAST
        (
            oc.CalculatedIqrUpperBound
            AS DECIMAL(18,4)
        ) AS IqrUpperBound,

        CAST
        (
            CASE
                WHEN oc.IsIqrOutlier = 1
                  OR oc.IsZScoreOutlier = 1
                    THEN 1
                ELSE 0
            END
            AS BIT
        ) AS IsOutlier,

        CASE
            WHEN oc.IsIqrOutlier = 1
             AND oc.IsZScoreOutlier = 1
                THEN 'IQR+ZSCORE'

            WHEN oc.IsIqrOutlier = 1
                THEN 'IQR'

            WHEN oc.IsZScoreOutlier = 1
                THEN 'ZSCORE'

            ELSE NULL
        END AS OutlierMethod

    INTO #FactAnalytics

    FROM OutlierClassification oc;

    /* ============================================================
       6. ATUALIZAR FATOS JÁ EXISTENTES

       A reexecução atualiza também os campos analíticos.
       ============================================================ */

    DECLARE @PipelineRunId UNIQUEIDENTIFIER = NEWID();

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
        fm.PipelineRunId = @PipelineRunId

    FROM gold.FactMeasurements fm

    INNER JOIN #FactAnalytics fa
        ON fa.ReadingValueId = fm.ReadingValueId;

    DECLARE @UpdatedFacts INT = @@ROWCOUNT;

    /* ============================================================
       7. INSERIR NOVOS FATOS
       ============================================================ */

    INSERT INTO gold.FactMeasurements
    (
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
        IsOutlier,
        OutlierMethod,

        LoadedAt,
        PipelineRunId
    )
    SELECT
        fa.StationKey,
        fa.ParameterKey,
        fa.DateKey,
        fa.TimeKey,

        fa.ReadingId,
        fa.ReadingValueId,
        fa.MeasurementDateTime,

        fa.MeasuredValue,
        fa.MovingAverageValue,
        fa.ZScore,
        fa.IqrLowerBound,
        fa.IqrUpperBound,
        fa.IsOutlier,
        fa.OutlierMethod,

        SYSUTCDATETIME(),
        @PipelineRunId

    FROM #FactAnalytics fa

    WHERE NOT EXISTS
    (
        SELECT 1
        FROM gold.FactMeasurements fm
        WHERE fm.ReadingValueId = fa.ReadingValueId
    );

    DECLARE @InsertedFacts INT = @@ROWCOUNT;

    COMMIT TRANSACTION;

    /* ============================================================
       8. RESUMO
       ============================================================ */

    SELECT
        @PipelineRunId AS PipelineRunId,
        @InsertedDates AS InsertedDates,
        @InsertedTimes AS InsertedTimes,
        @UpdatedFacts AS UpdatedFacts,
        @InsertedFacts AS InsertedFacts;

END TRY
BEGIN CATCH

    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;

END CATCH;
GO