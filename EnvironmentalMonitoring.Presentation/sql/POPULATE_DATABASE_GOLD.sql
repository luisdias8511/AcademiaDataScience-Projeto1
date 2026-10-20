USE EnvironmentalMonitoring;
GO

SET NOCOUNT ON;
GO

/* ============================================================
   DIM STATION
============================================================ */

INSERT INTO gold.DimStation
(
    StationId,
    StationCode,
    StationName,
    Latitude,
    Longitude,
    Municipality,
    State,
    Country
)
SELECT
    s.Id,
    s.Code,
    s.Name,
    s.Latitude,
    s.Longitude,
    s.Municipality,
    s.State,
    s.Country
FROM dbo.Stations s
WHERE NOT EXISTS
(
    SELECT 1
    FROM gold.DimStation ds
    WHERE ds.StationId = s.Id
);
GO


/* ============================================================
   DIM PARAMETER
============================================================ */

INSERT INTO gold.DimParameter
(
    ParameterId,
    ParameterCode,
    ParameterApiCode,
    ParameterName,
    Unit,
    CategoryId,
    CategoryCode,
    CategoryName
)
SELECT
    p.Id,
    p.Code,
    p.CodeApi,
    p.Name,
    p.Unit,
    pc.Id,
    pc.Code,
    pc.Name
FROM dbo.Parameters p
INNER JOIN dbo.ParameterCategories pc
    ON pc.Id = p.CategoryId
WHERE NOT EXISTS
(
    SELECT 1
    FROM gold.DimParameter dp
    WHERE dp.ParameterId = p.Id
);
GO

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
    20261012,
    '2026-10-12',
    2026,
    2,
    4,
    10,
    'Outubro',
    12,
    1,
    'Segunda-feira',
    0,
    1
WHERE NOT EXISTS
(
    SELECT 1
    FROM gold.DimDate
    WHERE DateKey = 20261012
);
GO

INSERT INTO gold.DimTime
(
    TimeKey,
    FullTime,
    HourNumber,
    MinuteNumber,
    SecondNumber
)
VALUES
(60000 ,'06:00:00',6 ,0,0),
(70000 ,'07:00:00',7 ,0,0),
(80000 ,'08:00:00',8 ,0,0),
(90000 ,'09:00:00',9 ,0,0),
(100000,'10:00:00',10,0,0),
(110000,'11:00:00',11,0,0);
GO
