USE EnvironmentalMonitoring;
GO
/*
========================================================
PARAMETER CATEGORIES
========================================================
*/

INSERT INTO dbo.ParameterCategories
(
    Code,
    Name
)
VALUES
('WEATHER', 'Parâmetros Meteorológicos'),
('WATER', 'Parâmetros de Qualidade da Água');
GO
/*
========================================================
PARAMETROS METEOROLOGICOS
========================================================
*/
USE EnvironmentalMonitoring;
GO
DECLARE @WeatherCategoryId INT;

SELECT @WeatherCategoryId = Id
FROM dbo.ParameterCategories
WHERE Code = 'WEATHER';

INSERT INTO dbo.Parameters
(
    Code,
    CodeApi,
    Name,
    Unit,
    CategoryId
)
VALUES
('AIR_TEMPERATURE', 'temperature', 'Temperatura do ar', '°C', @WeatherCategoryId);
GO

/*
========================================================
PARAMETROS HÍDRICOS
========================================================
*/
DECLARE @WaterCategoryId INT;
SELECT @WaterCategoryId = Id
FROM dbo.ParameterCategories
WHERE Code = 'WATER';

INSERT INTO dbo.Parameters
(
    Code,
    CodeApi,
    Name,
    Unit,
    CategoryId
)
VALUES
('CONDUCTIVITY','conductivity','Condutividade','µS/cm (25°C)',@WaterCategoryId),
('HARDNESS','hardness','Dureza da água','°f',@WaterCategoryId),
('TURBIDITY','turbidity','Turbidez','NFU',@WaterCategoryId),
('PH','ph','Potencial hidrogeniônico (pH)','pH unity',@WaterCategoryId),
('WATER_TEMPERATURE', 'temperature', 'Temperatura da água', '°C', @WaterCategoryId);


/*
========================================================
ESTACOES METEOROLOGICAS
========================================================
*/ 
 
INSERT INTO dbo.Stations
(
    Code,
    Name,
    Latitude,
    Longitude
)
VALUES

-- França
('FR_PARIS_488566_23522', 'Estação Paris', 48.8566, 2.3522)
-- ,
-- ('FR_MARSEILLE_432969_53698', 'Estação Marselha', 43.2965, 5.3698)
-- ,
-- ('FR_LYON_457640_48357', 'Estação Lyon', 45.7640, 4.8357)
-- ,
-- -- Reino Unido
-- ('UK_LONDON_515074_01278', 'Estação Londres', 51.5074, -0.1278)
;