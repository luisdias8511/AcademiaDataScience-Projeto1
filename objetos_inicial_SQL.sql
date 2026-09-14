/*
========================================================
BANCO: EnvironmentalMonitoring
========================================================
*/
IF NOT EXISTS (
    SELECT *
    FROM sys.databases
    WHERE name = 'EnvironmentalMonitoring'
)
BEGIN
    CREATE DATABASE EnvironmentalMonitoring;
END
GO
USE EnvironmentalMonitoring;
GO
/*
========================================================
TABELA ESTACOES
========================================================
*/
--DROP TABLE IF EXISTS dbo.Estacoes;

CREATE TABLE dbo.Estacoes
(
    Id  INT IDENTITY(1,1) NOT NULL,
    Codigo  VARCHAR(50) NOT NULL,
    Nome    VARCHAR(200) NOT NULL,
    Latitude    DECIMAL(10,6) NOT NULL,
    Longitude   DECIMAL(10,6) NOT NULL,

    CONSTRAINT PK_Estacoes PRIMARY KEY (Id),
    CONSTRAINT UQ_Estacoes_Codigo UNIQUE (Codigo)
);
GO
/*
========================================================
TABELA LEITURAS
========================================================
*/
CREATE TABLE dbo.Leituras
(
    Id  BIGINT IDENTITY(1,1) NOT NULL,
    EstacaoId   INT NOT NULL,
    DataHora    DATETIME2(0) NOT NULL

    CONSTRAINT DF_Leituras_DataCarga DEFAULT GETDATE(),
    CONSTRAINT PK_Leituras PRIMARY KEY (Id),
    CONSTRAINT FK_Leituras_Estacoes FOREIGN KEY (EstacaoId) REFERENCES dbo.Estacoes(Id)
);
GO
/*
========================================================
TABELA PARAMETROS
========================================================
*/
CREATE TABLE dbo.Parametros
(
    Id INT IDENTITY(1,1) NOT NULL,
    Codigo VARCHAR(50) NOT NULL,
    Nome VARCHAR(150) NOT NULL,
    Unidade VARCHAR(20) NULL,

    CONSTRAINT PK_Parametros PRIMARY KEY (Id),
    CONSTRAINT UQ_Parametros_Codigo UNIQUE (Codigo)
);
GO
/*
========================================================
TABELA VALORES_LEITURA
========================================================
*/
CREATE TABLE dbo.ValoresLeitura
(
    Id BIGINT IDENTITY(1,1) NOT NULL,
    LeituraId BIGINT NOT NULL,
    ParametroId INT NOT NULL,
    Valor DECIMAL(18,4) NOT NULL,
    
    CONSTRAINT PK_ValoresLeitura PRIMARY KEY (Id),
    CONSTRAINT FK_ValoresLeitura_Leituras FOREIGN KEY (LeituraId) REFERENCES dbo.Leituras(Id),
    CONSTRAINT FK_ValoresLeitura_Parametros FOREIGN KEY (ParametroId) REFERENCES dbo.Parametros(Id),
    CONSTRAINT UQ_ValoresLeitura UNIQUE (LeituraId, ParametroId)
);
GO
/*
========================================================
INDICES
========================================================
*/
CREATE INDEX IX_Leituras_Estacao_Data ON dbo.Leituras(EstacaoId, DataHora);
GO

CREATE INDEX IX_ValoresLeitura_Parametro ON dbo.ValoresLeitura(ParametroId);
GO

CREATE INDEX IX_ValoresLeitura_Leitura ON dbo.ValoresLeitura(LeituraId);
GO
/*
========================================================
PARAMETROS METEOROLOGICOS
========================================================
*/
INSERT INTO dbo.Parametros
(
    Codigo,
    Nome,
    Unidade
)
VALUES
('APPARENT_TEMPERATURE',
 'Apparent Temperature',
 '°C'),
('CLOUD_COVER',
 'Cloud Cover',
 '%'),
('HUMIDITY',
 'Humidity',
 '%'),
('PRECIPITATIONS',
 'Precipitations',
 'mm'),
('PRESSURE',
 'Pressure',
 'hPa'),
('TEMPERATURE',
 'Temperature',
 '°C'),
('WIND_DIRECTION',
 'Wind Direction',
 '°'),
('WIND_SPEED',
 'Wind Speed',
 'km/h'),
('PH',
 'pH',
 NULL);
GO
 
 
 SELECT
    *
 FROM dbo.Parametros;
 
 
 INSERT INTO dbo.Estacoes
(
    Codigo,
    Nome,
    Latitude,
    Longitude
)
VALUES
('MG_BH_1992083_4393778', 'Estação Belo Horizonte', -19.92083, -43.93778),
('RJ_RIO_229068_431729', 'Estação Rio de Janeiro', -22.9068, -43.1729),
('SP_PAULINIA_227611_471542', 'Estação Paulinia', -22.7611, -47.1542),
('SP_SP_283878_539147', 'Estação São Paulo', -28.3878, -53.9147)
;
GO
 
 SELECT
    *
 FROM dbo.Estacoes;