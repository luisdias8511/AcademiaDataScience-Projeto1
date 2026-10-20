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

-- França
('FR_PARIS_488566_23522', 'Estação Paris', 48.8566, 2.3522, 'Paris', 'Île-de-France', 'France')
-- ,
-- ('FR_MARSEILLE_432969_53698', 'Estação Marselha', 43.2965, 5.3698, 'Marseille', 'Provence-Alpes-Côte d\'Azur', 'France')
-- ,
-- ('FR_LYON_457640_48357', 'Estação Lyon', 45.7640, 4.8357, 'Lyon', 'Auvergne-Rhône-Alpes', 'France')
-- ,
-- -- Reino Unido
-- ('UK_LONDON_515074_01278', 'Estação Londres', 51.5074, -0.1278, 'London', 'England', 'United Kingdom')
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
    ('Sass', 'pbkdf2_sha256$600000$1zdqA5+W8hp835UXuKXEBw==$fTpQgTefQrRw8xDc6XAYyep9k+yP7hXlj9C0TR4GgEM=', '926e1bff30a6f8dfb2bd4d967c5ffc3af531fa071dcdbe3857fe98da979121be', 'gAAAAABq1qIyvzqGLQ1PL6l8XX-d2JpwjQx52dlgw1mf6jlRU1yTgmVXTZGd37EKHGXm6d4RJNttGpmXUrf429Hycgwl0d_xig==', 'gAAAAABq1qIyFPn35VZQIPYJv6zsmx4ZIjz_W8YBedzIO1yoAPJzYOHwVW3bQdDVvFvsg52djcf2Lb2wk0UFK-Mc_-mSfUVa0g==', 'gAAAAABq1qIyi83XQfDKdnrLg1oMxvgXaVzYTuV7UKaTuUMP7VdAOowqOItWBvOCtdiSeJUCLNvOqS5s0C8-LOWGgVkq9TBYDw==', 'Adm', GETDATE()),
     ('Teste10', 'pbkdf2_sha256$600000$HsrtWRV5lfOwQ7fA6cY6tQ==$pFOyavnsU5PoNc2oX/wSj+vuL449NY/IK20PGJX2EZc=', 'b59bd87589b6926d20dcd82b55aca32b094bc131e203bbf76fb30d186a13ba78', 'gAAAAABq1pZHxMdJnqOBHkBuR-D0fiSz8unmPfl_m0b8nQtqxbRoirGsPhsCHJ2MlVjkgA3XW5aAyNTi-NbLcPEwOXYjDToYuQ==', 'gAAAAABq1pZH_Uj4PctWlGjRrGUs6vYXMzJxloy1voOqVKpn3TYHOnD-RdtECYFitaAZtISnCF3kJXLdA_zOkcJ1cJBB_uXw5w==', 'gAAAAABq1pZHYdHzZlFzsJLelJhEbzuXbQwwMrZNSPqJ6uRjU03YWrH0oLntEQodZZlYu6Qg7q0C-FL5YD9LrX02QzYLMVBHCA==', 'Operador10', GETDATE());
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
    ServiceId
)
VALUES
(1, null),
(null, 1);
GO
