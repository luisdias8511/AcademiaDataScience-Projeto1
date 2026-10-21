/*
========================================================
APAGAR TABELAS EXISTENTES
========================================================
*/
USE EnvironmentalMonitoring;
GO

IF OBJECT_ID('dbo.ReadingValues', 'U') IS NOT NULL
    DROP TABLE dbo.ReadingValues;
GO

IF OBJECT_ID('dbo.Readings', 'U') IS NOT NULL
    DROP TABLE dbo.Readings;
GO

IF OBJECT_ID('dbo.Parameters', 'U') IS NOT NULL
    DROP TABLE dbo.Parameters;
GO

IF OBJECT_ID('dbo.Stations', 'U') IS NOT NULL
    DROP TABLE dbo.Stations;
GO

IF OBJECT_ID('dbo.ParameterCategories', 'U') IS NOT NULL
    DROP TABLE dbo.ParameterCategories;
GO
IF OBJECT_ID('dbo.Operators', 'U') IS NOT NULL
    DROP TABLE dbo.Operators;
GO

IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL
    DROP TABLE dbo.Users;
GO

IF OBJECT_ID('dbo.Services', 'U') IS NOT NULL
    DROP TABLE dbo.Services;
GO

/*
========================================================
STATIONS TABLE
========================================================
*/

CREATE TABLE dbo.Stations
(
    Id  INT IDENTITY(1,1) NOT NULL,
    Code  VARCHAR(50) NOT NULL,
    Name    VARCHAR(200) NOT NULL,
    Latitude    DECIMAL(10,6) NOT NULL,
    Longitude   DECIMAL(10,6) NOT NULL,
    Municipality VARCHAR(100) NOT NULL,
    State VARCHAR(50) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    CONSTRAINT PK_Stations PRIMARY KEY (Id),
    CONSTRAINT UQ_Stations_Code UNIQUE (Code)
);
GO
/*
========================================================
USERS TABLE
========================================================
*/
CREATE TABLE dbo.Users
(
    Id INT IDENTITY(1,1) NOT NULL,
    Username VARCHAR(100) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Cpf VARCHAR(64) NOT NULL,
    FullName  VARCHAR(500)  NOT NULL,
    Email VARCHAR(500) NOT NULL,
    Phone VARCHAR(500) NULL,
    Atribution VARCHAR(100) NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Users PRIMARY KEY (Id),
    CONSTRAINT UQ_Users_Username UNIQUE (Username),
    CONSTRAINT UQ_Users_Email UNIQUE (Email),
    CONSTRAINT UQ_Users_Cpf UNIQUE (Cpf)
);
GO
/*
========================================================
SERVICES TABLE
========================================================
*/
CREATE TABLE dbo.Services
(
    Id INT IDENTITY(1,1) NOT NULL,
    Code VARCHAR(100) NOT NULL,
    Name VARCHAR(150) NOT NULL,

    CONSTRAINT PK_Services
        PRIMARY KEY (Id),
    CONSTRAINT UQ_Services_Code
        UNIQUE (Code)
);
GO
/*
========================================================
OPERATORS TABLE
========================================================
*/
CREATE TABLE dbo.Operators
(
    Id INT IDENTITY(1,1) NOT NULL,
    Code VARCHAR(100) NOT NULL UNIQUE,
    UserId INT NULL,
    ServiceId INT NULL,

    CONSTRAINT PK_Operators
        PRIMARY KEY (Id),
    CONSTRAINT FK_Operators_Users
        FOREIGN KEY (UserId)
        REFERENCES dbo.Users(Id),
    CONSTRAINT FK_Operators_Services
        FOREIGN KEY (ServiceId)
        REFERENCES dbo.Services(Id),

    CONSTRAINT CK_Operators_UserOrService
        CHECK
        (
            (UserId IS NOT NULL AND ServiceId IS NULL)
            OR
            (UserId IS NULL AND ServiceId IS NOT NULL)
        ),

    CONSTRAINT UQ_Operators_User
        UNIQUE (UserId),

    CONSTRAINT UQ_Operators_Service
        UNIQUE (ServiceId),

    CONSTRAINT UQ_Operators_Code
        UNIQUE (Code)
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
    DateTime    DATETIME2(0) NOT NULL,
    OperatorId INT NOT NULL,

    CONSTRAINT PK_Readings PRIMARY KEY (Id),
    CONSTRAINT FK_Readings_Stations FOREIGN KEY (StationId) REFERENCES dbo.Stations(Id),
    CONSTRAINT FK_Readings_Operators FOREIGN KEY (OperatorId) REFERENCES dbo.Operators(Id)
);
GO
/*
========================================================
PARAMETER CATEGORIES
========================================================
*/

CREATE TABLE dbo.ParameterCategories
(
    Id INT IDENTITY(1,1) NOT NULL,
    Code VARCHAR(50) NOT NULL,
    Name VARCHAR(150) NOT NULL,

    CONSTRAINT PK_ParameterCategories
        PRIMARY KEY (Id),

    CONSTRAINT UQ_ParameterCategories_Code
        UNIQUE (Code)
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

    Code VARCHAR(100) NOT NULL,
    CodeApi VARCHAR(100) NOT NULL,

    Name VARCHAR(150) NOT NULL,
    Unit VARCHAR(30) NULL,

    CategoryId INT NOT NULL,

    CONSTRAINT PK_Parameters
        PRIMARY KEY (Id),

    CONSTRAINT UQ_Parameters_Code
        UNIQUE (Code),

    CONSTRAINT FK_Parameters_ParameterCategories
        FOREIGN KEY (CategoryId)
        REFERENCES dbo.ParameterCategories(Id)
);
GO

/*
========================================================
READING VALUES TABLE
========================================================
*/
CREATE TABLE dbo.ReadingValues
(
    ReadingId BIGINT NOT NULL,
    ParameterId INT NOT NULL,
    Value DECIMAL(18,4) NOT NULL,
    
    CONSTRAINT PK_ReadingValues PRIMARY KEY (ReadingId, ParameterId),
    CONSTRAINT FK_ReadingValues_Readings FOREIGN KEY (ReadingId) REFERENCES dbo.Readings(Id),
    CONSTRAINT FK_ReadingValues_Parameters FOREIGN KEY (ParameterId) REFERENCES dbo.Parameters(Id)
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
