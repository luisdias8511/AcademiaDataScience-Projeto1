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
    Longitude,
    Municipality,
    State,
    Country
)
VALUES
('FR_PARIS_488566_23522', 'Estação Paris', 48.8566, 2.3522, 'Paris', 'Île-de-France', 'França'),
('FR_MARSEILLE_432969_53698', 'Estação Marselha', 43.2965, 5.3698, 'Marselha', 'Provence-Alpes-Côte dAzur', 'França'),
('FR_LYON_457640_48357', 'Estação Lyon', 45.7640, 4.8357, 'Lyon', 'Auvergne-Rhône-Alpes', 'França'),
('FR_TOULOUSE_436044_14433', 'Estação Toulouse', 43.6044, 1.4433, 'Toulouse', 'Occitânia', 'França'),
('FR_NICE_437019_72683', 'Estação Nice', 43.7019, 7.2683, 'Nice', 'Provence-Alpes-Côte dAzur', 'França')
;

/*
========================================================
USUARIOS
========================================================
*/ 

INSERT INTO dbo.Users
(
    Username,
    PasswordHash,
    Cpf,
    FullName,
    Email,
    Phone,
    Atribution,
    CreatedAt
)
VALUES
    ('username', 
    '******', 
    '******', 
    '******', 
    '******', 
    '******', 
    'Adm', 
    GETDATE());     
/*
========================================================
SERVICES
========================================================
*/
INSERT INTO dbo.Services
(
    Code,
    Name
)
VALUES
('MEERSENS', 'Serviço Meteorológico e Hídrico da MeerSens');
GO

/*
========================================================
OPERATORS
========================================================
*/
INSERT INTO dbo.Operators
(
    UserId,
    ServiceId,
    Code
)
VALUES
(1, null, 'OP_USER_SASS'),
(null, 1, 'OP_SERVICE_MEERSENS');
GO