/* ============================================================================
   GOLD - STAR SCHEMA | EnvironmentalMonitoring
   SQL Server Express / Azure SQL Database

   Silver source:
     dbo.Stations
     dbo.ParameterCategories
     dbo.Parameters
     dbo.Readings
     dbo.ReadingValues

   Fact grain:
     One row per parameter value measured at a station at a given timestamp.

   Scope:
     DDL only. ETL/ELT, moving average, IQR and Z-Score are handled outside
     this script and subsequently loaded into the fact table.
   ============================================================================ */

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'gold')
    EXEC('CREATE SCHEMA gold AUTHORIZATION dbo;');
GO

/* ============================================================================
   DIM STATION
   ============================================================================ */
CREATE TABLE gold.DimStation
(
    StationKey   INT IDENTITY(1,1) NOT NULL,
    StationId    INT NOT NULL,              -- Natural key from Silver
    StationCode  VARCHAR(50) NOT NULL,
    StationName  VARCHAR(200) NOT NULL,
    Latitude     DECIMAL(10,6) NOT NULL,
    Longitude    DECIMAL(10,6) NOT NULL,

    CONSTRAINT PK_DimStation PRIMARY KEY CLUSTERED (StationKey),
    CONSTRAINT UQ_DimStation_StationId UNIQUE (StationId),
    CONSTRAINT UQ_DimStation_StationCode UNIQUE (StationCode)
);
GO

/* ============================================================================
   DIM PARAMETER
   ParameterCategories is denormalized into this dimension to keep a true star.
   ============================================================================ */
CREATE TABLE gold.DimParameter
(
    ParameterKey      INT IDENTITY(1,1) NOT NULL,
    ParameterId       INT NOT NULL,              -- Natural key from Silver
    ParameterCode     VARCHAR(100) NOT NULL,
    ParameterApiCode  VARCHAR(100) NOT NULL,
    ParameterName     VARCHAR(150) NOT NULL,
    Unit              VARCHAR(30) NULL,
    CategoryId        INT NOT NULL,
    CategoryCode      VARCHAR(50) NOT NULL,
    CategoryName      VARCHAR(150) NOT NULL,

    CONSTRAINT PK_DimParameter PRIMARY KEY CLUSTERED (ParameterKey),
    CONSTRAINT UQ_DimParameter_ParameterId UNIQUE (ParameterId),
    CONSTRAINT UQ_DimParameter_ParameterCode UNIQUE (ParameterCode)
);
GO

/* ============================================================================
   DIM DATE
   DateKey format: YYYYMMDD, e.g. 20261019.
   Holiday-aware business days may be added later by the ETL/calendar source.
   ============================================================================ */
CREATE TABLE gold.DimDate
(
    DateKey           INT NOT NULL,
    FullDate          DATE NOT NULL,
    CalendarYear      SMALLINT NOT NULL,
    CalendarSemester  TINYINT NOT NULL,
    CalendarQuarter   TINYINT NOT NULL,
    MonthNumber       TINYINT NOT NULL,
    MonthName         VARCHAR(20) NOT NULL,
    DayOfMonth        TINYINT NOT NULL,
    DayOfWeekNumber   TINYINT NOT NULL,
    DayOfWeekName     VARCHAR(20) NOT NULL,
    IsWeekend         BIT NOT NULL,
    IsBusinessDay     BIT NOT NULL,

    CONSTRAINT PK_DimDate PRIMARY KEY CLUSTERED (DateKey),
    CONSTRAINT UQ_DimDate_FullDate UNIQUE (FullDate),
    CONSTRAINT CK_DimDate_Semester CHECK (CalendarSemester BETWEEN 1 AND 2),
    CONSTRAINT CK_DimDate_Quarter CHECK (CalendarQuarter BETWEEN 1 AND 4),
    CONSTRAINT CK_DimDate_Month CHECK (MonthNumber BETWEEN 1 AND 12),
    CONSTRAINT CK_DimDate_DayOfWeek CHECK (DayOfWeekNumber BETWEEN 1 AND 7)
);
GO

/* ============================================================================
   DIM TIME
   TimeKey format: HHMMSS, e.g. 081537.
   ============================================================================ */
CREATE TABLE gold.DimTime
(
    TimeKey       INT NOT NULL,
    FullTime      TIME(0) NOT NULL,
    HourNumber    TINYINT NOT NULL,
    MinuteNumber  TINYINT NOT NULL,
    SecondNumber  TINYINT NOT NULL,

    CONSTRAINT PK_DimTime PRIMARY KEY CLUSTERED (TimeKey),
    CONSTRAINT UQ_DimTime_FullTime UNIQUE (FullTime),
    CONSTRAINT CK_DimTime_Hour CHECK (HourNumber BETWEEN 0 AND 23),
    CONSTRAINT CK_DimTime_Minute CHECK (MinuteNumber BETWEEN 0 AND 59),
    CONSTRAINT CK_DimTime_Second CHECK (SecondNumber BETWEEN 0 AND 59)
);
GO

/* ============================================================================
   FACT MEASUREMENTS

   ReadingValueId is retained for lineage/idempotency because a Silver
   ReadingValues row represents one parameter value of one reading.
   ============================================================================ */
CREATE TABLE gold.FactMeasurements
(
    MeasurementKey       BIGINT IDENTITY(1,1) NOT NULL,

    StationKey           INT NOT NULL,
    ParameterKey         INT NOT NULL,
    DateKey              INT NOT NULL,
    TimeKey              INT NOT NULL,

    ReadingId            BIGINT NOT NULL,
    ReadingValueId       BIGINT NOT NULL,
    MeasurementDateTime  DATETIME2(0) NOT NULL,

    MeasuredValue        DECIMAL(18,4) NOT NULL,

    /* Analytical attributes calculated by the processing pipeline. */
    MovingAverageValue   DECIMAL(18,4) NULL,
    ZScore               DECIMAL(18,6) NULL,
    IqrLowerBound        DECIMAL(18,4) NULL,
    IqrUpperBound        DECIMAL(18,4) NULL,
    IsOutlier            BIT NULL,
    OutlierMethod        VARCHAR(20) NULL,

    LoadedAt             DATETIME2(0) NOT NULL
        CONSTRAINT DF_FactMeasurements_LoadedAt DEFAULT SYSUTCDATETIME(),
    PipelineRunId        UNIQUEIDENTIFIER NULL,

    CONSTRAINT PK_FactMeasurements
        PRIMARY KEY CLUSTERED (MeasurementKey),

    CONSTRAINT UQ_FactMeasurements_ReadingValueId
        UNIQUE (ReadingValueId),

    CONSTRAINT FK_FactMeasurements_DimStation
        FOREIGN KEY (StationKey)
        REFERENCES gold.DimStation(StationKey),

    CONSTRAINT FK_FactMeasurements_DimParameter
        FOREIGN KEY (ParameterKey)
        REFERENCES gold.DimParameter(ParameterKey),

    CONSTRAINT FK_FactMeasurements_DimDate
        FOREIGN KEY (DateKey)
        REFERENCES gold.DimDate(DateKey),

    CONSTRAINT FK_FactMeasurements_DimTime
        FOREIGN KEY (TimeKey)
        REFERENCES gold.DimTime(TimeKey),

    CONSTRAINT CK_FactMeasurements_OutlierMethod
        CHECK (
            OutlierMethod IS NULL
            OR OutlierMethod IN ('IQR', 'ZSCORE', 'IQR+ZSCORE')
        ),

    CONSTRAINT CK_FactMeasurements_IqrBounds
        CHECK (
            IqrLowerBound IS NULL
            OR IqrUpperBound IS NULL
            OR IqrLowerBound <= IqrUpperBound
        )
);
GO

/* ============================================================================
   FACT INDEXES FOR THE MAIN ANALYTICAL ACCESS PATHS
   ============================================================================ */
CREATE INDEX IX_FactMeasurements_Date_Station_Parameter
    ON gold.FactMeasurements
       (DateKey, StationKey, ParameterKey)
    INCLUDE
       (MeasuredValue, IsOutlier, MeasurementDateTime);
GO

CREATE INDEX IX_FactMeasurements_Station_Parameter_DateTime
    ON gold.FactMeasurements
       (StationKey, ParameterKey, MeasurementDateTime)
    INCLUDE
       (MeasuredValue, MovingAverageValue, IsOutlier);
GO
