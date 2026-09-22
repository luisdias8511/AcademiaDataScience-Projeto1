/*
========================================================
STATIONS TABLE
========================================================
*/
--DROP TABLE IF EXISTS dbo.Stations;

CREATE TABLE dbo.Stations
(
    Id  INT IDENTITY(1,1) NOT NULL,
    Code  VARCHAR(50) NOT NULL,
    Name    VARCHAR(200) NOT NULL,
    Latitude    DECIMAL(10,6) NOT NULL,
    Longitude   DECIMAL(10,6) NOT NULL,

    CONSTRAINT PK_Stations PRIMARY KEY (Id),
    CONSTRAINT UQ_Stations_Code UNIQUE (Code)
);
GO
/*
========================================================
READINGS TABLE
========================================================
*/
CREATE TABLE dbo.Readings
(
    Id  BIGINT IDENTITY(1,1) NOT NULL,
    StationId   INT NOT NULL,
    DateTime    DATETIME2(0) NOT NULL

    CONSTRAINT DF_Readings_LoadDate DEFAULT GETDATE(),
    CONSTRAINT PK_Readings PRIMARY KEY (Id),
    CONSTRAINT FK_Readings_Stations FOREIGN KEY (StationId) REFERENCES dbo.Stations(Id)
);
GO
/*
========================================================
PARAMETERS TABLE
========================================================
*/
CREATE TABLE dbo.Parameters
(
    Id INT IDENTITY(1,1) NOT NULL,
    Code VARCHAR(50) NOT NULL,
    Name VARCHAR(150) NOT NULL,
    Unit VARCHAR(20) NULL,

    CONSTRAINT PK_Parameters PRIMARY KEY (Id),
    CONSTRAINT UQ_Parameters_Code UNIQUE (Code)
);
GO
/*
========================================================
READING VALUES TABLE
========================================================
*/
CREATE TABLE dbo.ReadingValues
(
    Id BIGINT IDENTITY(1,1) NOT NULL,
    ReadingId BIGINT NOT NULL,
    ParameterId INT NOT NULL,
    Value DECIMAL(18,4) NOT NULL,
    
    CONSTRAINT PK_ReadingValues PRIMARY KEY (Id),
    CONSTRAINT FK_ReadingValues_Readings FOREIGN KEY (ReadingId) REFERENCES dbo.Readings(Id),
    CONSTRAINT FK_ReadingValues_Parameters FOREIGN KEY (ParameterId) REFERENCES dbo.Parameters(Id),
    CONSTRAINT UQ_ReadingValues UNIQUE (ReadingId, ParameterId)
);
GO
/*
========================================================
INDICES
========================================================
*/
CREATE INDEX IX_Readings_Station_DateTime ON dbo.Readings(StationId, DateTime);
GO

CREATE INDEX IX_ReadingValues_Parameter ON dbo.ReadingValues(ParameterId);
GO

CREATE INDEX IX_ReadingValues_Reading ON dbo.ReadingValues(ReadingId);
GO
