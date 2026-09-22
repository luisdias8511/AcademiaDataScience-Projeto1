/*
========================================================
PARAMETROS METEOROLOGICOS
========================================================
*/
INSERT INTO dbo.Parameters
(
    Code,
    Name,
    Unit
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
 FROM dbo.Parameters;
 
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
('MG_BH_1992083_4393778', 'Estação Belo Horizonte', -19.92083, -43.93778),
('RJ_RIO_229068_431729', 'Estação Rio de Janeiro', -22.9068, -43.1729),
('SP_PAULINIA_227611_471542', 'Estação Paulinia', -22.7611, -47.1542),
('SP_SP_283878_539147', 'Estação São Paulo', -28.3878, -53.9147),
('RS_PORTO_ALEGRE_30033056_51230000', 'Estação Porto Alegre', -30.033056, -51.230000)
;
GO
 
 SELECT
    *
 FROM dbo.Stations;