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
(
    'WEATHER',
    'Parâmetros Meteorológicos'
),
(
    'WATER',
    'Parâmetros de Qualidade da Água'
);
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

('APPARENT_TEMPERATURE',
 'apparent_temperature',
 'Temperatura aparente',
 '°C',
 @WeatherCategoryId),

('CLOUD_COVER',
 'cloud_cover',
 'Cobertura de nuvens',
 '%',
 @WeatherCategoryId),

('HUMIDITY',
 'humidity',
 'Umidade',
 '%',
 @WeatherCategoryId),

('PRECIPITATIONS',
 'precipitations',
 'Precipitações',
 'mm',
 @WeatherCategoryId),

('PRESSURE',
 'pressure',
 'Pressão atmosférica',
 'hPa',
 @WeatherCategoryId),

('AIR_TEMPERATURE',
 'temperature',
 'Temperatura do ar',
 '°C',
 @WeatherCategoryId),

('WIND_DIRECTION',
 'wind_direction',
 'Direção do vento',
 '°',
 @WeatherCategoryId),

('WIND_SPEED',
 'wind_speed',
 'Velocidade do vento',
 'km/h',
 @WeatherCategoryId);
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

('NITRATES','nitrates','Nitratos','mg/L',@WaterCategoryId),
('PESTICIDES','pesticides','Pesticidas totais','µg/L',@WaterCategoryId),
('ARSENIC','arsenic','Arsênio','µg/L',@WaterCategoryId),
('SELENIUM','selenium','Selênio','µg/L',@WaterCategoryId),
('BROMATES','bromates','Bromatos','µg/L',@WaterCategoryId),
('TOTAL_ALUMINIUM','total aluminium','Alumínio total','µg/L',@WaterCategoryId),
('IRON','iron','Ferro','µg/L',@WaterCategoryId),
('FLUORIDES','fluorides','Fluoretos','mg/L',@WaterCategoryId),
('PAHS','pahs','Hidrocarbonetos aromáticos policíclicos','µg/L',@WaterCategoryId),
('ACRYLAMIDE','acrylamide','Acrilamida','µg/L',@WaterCategoryId),
('BARIUM','barium','Bário','µg/L',@WaterCategoryId),
('BENZENE','benzene','Benzeno','µg/L',@WaterCategoryId),
('BORON','boron','Boro','mg/L',@WaterCategoryId),
('CADMIUM','cadmium','Cádmio','µg/L',@WaterCategoryId),
('TOTAL_CHROMIUM','total chromium','Cromo total','µg/L',@WaterCategoryId),
('EPICHLOROHYDRIN','epichlorohydrin','Epicloridrina','µg/L',@WaterCategoryId),
('MERCURY','mercury','Mercúrio','µg/L',@WaterCategoryId),
('MICROCYSTIN_LR','microcystin-lr','Microcistina LR','µg/L',@WaterCategoryId),
('TETRACHLOROETHYLENE_AND_TRICHLOROETHYLENE',
 'tetrachloroethylene and trichloroethylene',
 'Tetracloroetileno e Tricloroetileno',
 'µg/L',
 @WaterCategoryId),

('THMS','thms','Trihalometanos','µg/L',@WaterCategoryId),
('AMMONIUM','ammonium','Amônio','mg/L',@WaterCategoryId),
('SODIUM','sodium','Sódio','mg/L',@WaterCategoryId),
('SULPHATES','sulphates','Sulfatos','µg/L',@WaterCategoryId),
('FREE_CHLORINE','free_chlorine','Cloro livre','mg(Cl2)/L',@WaterCategoryId),
('CHLORIDES','chlorides','Cloretos','mg/L',@WaterCategoryId),
('NITRITES','nitrites','Nitritos','mg/L',@WaterCategoryId),
('MANGANESE','manganese','Manganês','µg/L',@WaterCategoryId),
('CALCIUM','calcium','Cálcio','mg/L',@WaterCategoryId),
('CONDUCTIVITY','conductivity','Condutividade','µS/cm (25°C)',@WaterCategoryId),
('MAGNESIUM','magnesium','Magnésio','mg/L',@WaterCategoryId),
('HARDNESS','hardness','Dureza da água','°f',@WaterCategoryId),
('TURBIDITY','turbidity','Turbidez','NFU',@WaterCategoryId),
('PH','ph','Potencial hidrogeniônico (pH)','pH unity',@WaterCategoryId),
('NICKEL','nickel','Níquel','µg/L',@WaterCategoryId),
('COPPER','copper','Cobre','µg/L',@WaterCategoryId),
('BAP','bap','Benzo[a]pireno','µg/L',@WaterCategoryId),
('PCB','pcb','Bifenilos policlorados','µg/L',@WaterCategoryId),
('TRITIUM','tritium','Trítio','Bq/L',@WaterCategoryId),
('RADON','radon','Radônio','Bq/L',@WaterCategoryId),

('WATER_TEMPERATURE',
 'temperature',
 'Temperatura da água',
 '°C',
 @WaterCategoryId),

('TOTAL_CHLORINE',
 'total_chlorine',
 'Cloro total',
 'mg(Cl2)/L',
 @WaterCategoryId),

('COLIFORM',
 'coliform',
 'Bactérias coliformes',
 '/100mL',
 @WaterCategoryId),

('COLI',
 'coli',
 'Escherichia coli',
 '/100mL',
 @WaterCategoryId),

('ENTEROCOCCI',
 'enterococci',
 'Enterococos',
 '/100mL',
 @WaterCategoryId),

('CHLORITES',
 'chlorites',
 'Cloritos',
 'mg/L',
 @WaterCategoryId);


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

-- Reino Unido
('UK_LONDON_515074_01278', 'Estação Londres', 51.5074, -0.1278),
('UK_BIRMINGHAM_524861_01898', 'Estação Birmingham', 52.4861, -1.8904),
('UK_BRIGHTON_508227_01558', 'Estação Brighton', 50.8225, -0.1558),

-- França
('FR_PARIS_488566_23522', 'Estação Paris', 48.8566, 2.3522),
('FR_MARSEILLE_432969_53698', 'Estação Marselha', 43.2965, 5.3698),
('FR_LYON_457640_48357', 'Estação Lyon', 45.7640, 4.8357);
GO
 
 SELECT
    *
 FROM dbo.Stations;