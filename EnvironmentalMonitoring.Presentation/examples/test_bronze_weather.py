import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ingestion.bronze_weather_transformer import build_bronze_documents_weather
from src.database.reading_repository import ReadingRepository

# Inicializa o repositório conexao com o banco de dados
repository = ReadingRepository()
# Obtem os parâmetros permitidos para parâmetros de clima
allowed_parameters = repository.get_parameters_by_CategoryCode("WEATHER")

# JSON de EXEMPLO retornado pela API Meersens para parâmetros de clima
# TEM QUE ESTAR ENTRE ASPAS TRIPLAS (''' ''')
meersens_json = '''
{
    "found": true,
    "values": [
        {
            "found": true,
            "datetime": "2026-10-12T17:00:00.000Z",
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Correct",
                "icon": null,
                "color": "#44b001",
                "description": "Correct weather",
                "value": 28.77,
                "main_pollutants": [
                    "humidity"
                ]
            },
            "parameters": {
                "apparent_temperature": {
                    "shortcode": "aT",
                    "name": "Apparent temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.74,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "No adverse effects expected with right outfits and/or equipment",
                        "value": 3.22
                    }
                },
                "cloud_cover": {
                    "shortcode": "CC",
                    "name": "Cloud cover",
                    "found": true,
                    "confidence": 4.5,
                    "value": 98,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "humidity": {
                    "shortcode": "rH",
                    "name": "Humidity",
                    "found": true,
                    "confidence": 4.5,
                    "value": 89.42,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Correct",
                        "icon": null,
                        "color": "#44b001",
                        "description": "Wet atmosphere",
                        "value": 28.77
                    }
                },
                "precipitations": {
                    "shortcode": "Pc",
                    "name": "Precipitations",
                    "found": true,
                    "confidence": 4.5,
                    "unit": "mm",
                    "value": 0,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "No precipitation",
                        "value": 5
                    }
                },
                "pressure": {
                    "shortcode": "P",
                    "name": "Pressure",
                    "found": true,
                    "confidence": 4.5,
                    "value": 1000.31,
                    "unit": "hPa",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Depression: unsettled weather",
                        "value": 4.88
                    }
                },
                "temperature": {
                    "shortcode": "T",
                    "name": "Temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.74,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Low",
                        "icon": null,
                        "color": "#029a8d",
                        "description": "Chilly temperature",
                        "value": 21.02
                    }
                },
                "wind_direction": {
                    "shortcode": "Wd",
                    "name": "Wind direction",
                    "found": true,
                    "confidence": 4.5,
                    "value": -7.73,
                    "unit": "°",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "wind_speed": {
                    "shortcode": "Ws",
                    "name": "Wind speed",
                    "found": true,
                    "confidence": 4.5,
                    "value": 13.18,
                    "unit": "km/h",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "Light to moderate breezes",
                        "value": 12.69
                    }
                },
                "ww": {
                    "shortcode": "WW",
                    "name": "Significant weather",
                    "found": true,
                    "confidence": 4.5,
                    "qualification": "Cloudy",
                    "description": "Clouds generally forming or developing",
                    "icon": "https://s3.eu-west-2.amazonaws.com/weather.meersens/icons/cloudy.png",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                }
            }
        },
        {
            "found": true,
            "datetime": "2026-10-12T18:00:00.000Z",
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Correct",
                "icon": null,
                "color": "#44b001",
                "description": "Correct weather",
                "value": 30.13,
                "main_pollutants": [
                    "humidity"
                ]
            },
            "parameters": {
                "apparent_temperature": {
                    "shortcode": "aT",
                    "name": "Apparent temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.62,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "No adverse effects expected with right outfits and/or equipment",
                        "value": 3.2
                    }
                },
                "cloud_cover": {
                    "shortcode": "CC",
                    "name": "Cloud cover",
                    "found": true,
                    "confidence": 4.5,
                    "value": 97,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "humidity": {
                    "shortcode": "rH",
                    "name": "Humidity",
                    "found": true,
                    "confidence": 4.5,
                    "value": 92.82,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Correct",
                        "icon": null,
                        "color": "#44b001",
                        "description": "Wet atmosphere",
                        "value": 30.13
                    }
                },
                "precipitations": {
                    "shortcode": "Pc",
                    "name": "Precipitations",
                    "found": true,
                    "confidence": 4.5,
                    "unit": "mm",
                    "value": 0,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "No precipitation",
                        "value": 5
                    }
                },
                "pressure": {
                    "shortcode": "P",
                    "name": "Pressure",
                    "found": true,
                    "confidence": 4.5,
                    "value": 1000.3,
                    "unit": "hPa",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Depression: unsettled weather",
                        "value": 4.88
                    }
                },
                "temperature": {
                    "shortcode": "T",
                    "name": "Temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.62,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Low",
                        "icon": null,
                        "color": "#029a8d",
                        "description": "Chilly temperature",
                        "value": 21.23
                    }
                },
                "wind_direction": {
                    "shortcode": "Wd",
                    "name": "Wind direction",
                    "found": true,
                    "confidence": 4.5,
                    "value": 1.69,
                    "unit": "°",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "wind_speed": {
                    "shortcode": "Ws",
                    "name": "Wind speed",
                    "found": true,
                    "confidence": 4.5,
                    "value": 14.24,
                    "unit": "km/h",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "Light to moderate breezes",
                        "value": 13.36
                    }
                },
                "ww": {
                    "shortcode": "WW",
                    "name": "Significant weather",
                    "found": true,
                    "confidence": 4.5,
                    "qualification": "Cloudy",
                    "description": "Clouds generally forming or developing",
                    "icon": "https://s3.eu-west-2.amazonaws.com/weather.meersens/icons/cloudy.png",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                }
            }
        },
        {
            "found": true,
            "datetime": "2026-10-12T19:00:00.000Z",
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Correct",
                "icon": null,
                "color": "#44b001",
                "description": "Correct weather",
                "value": 31.42,
                "main_pollutants": [
                    "humidity"
                ]
            },
            "parameters": {
                "apparent_temperature": {
                    "shortcode": "aT",
                    "name": "Apparent temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.41,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "No adverse effects expected with right outfits and/or equipment",
                        "value": 3.16
                    }
                },
                "cloud_cover": {
                    "shortcode": "CC",
                    "name": "Cloud cover",
                    "found": true,
                    "confidence": 4.5,
                    "value": 87,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "humidity": {
                    "shortcode": "rH",
                    "name": "Humidity",
                    "found": true,
                    "confidence": 4.5,
                    "value": 96.04,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Correct",
                        "icon": null,
                        "color": "#44b001",
                        "description": "Wet atmosphere",
                        "value": 31.42
                    }
                },
                "precipitations": {
                    "shortcode": "Pc",
                    "name": "Precipitations",
                    "found": true,
                    "confidence": 4.5,
                    "unit": "mm",
                    "value": 0,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "No precipitation",
                        "value": 5
                    }
                },
                "pressure": {
                    "shortcode": "P",
                    "name": "Pressure",
                    "found": true,
                    "confidence": 4.5,
                    "value": 1000.99,
                    "unit": "hPa",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Depression: unsettled weather",
                        "value": 4.62
                    }
                },
                "temperature": {
                    "shortcode": "T",
                    "name": "Temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.41,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Low",
                        "icon": null,
                        "color": "#029a8d",
                        "description": "Chilly temperature",
                        "value": 21.6
                    }
                },
                "wind_direction": {
                    "shortcode": "Wd",
                    "name": "Wind direction",
                    "found": true,
                    "confidence": 4.5,
                    "value": 2.59,
                    "unit": "°",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "wind_speed": {
                    "shortcode": "Ws",
                    "name": "Wind speed",
                    "found": true,
                    "confidence": 4.5,
                    "value": 12.93,
                    "unit": "km/h",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "Light to moderate breezes",
                        "value": 12.53
                    }
                },
                "ww": {
                    "shortcode": "WW",
                    "name": "Significant weather",
                    "found": true,
                    "confidence": 4.5,
                    "qualification": "Cloudy",
                    "description": "Clouds generally forming or developing",
                    "icon": "https://s3.eu-west-2.amazonaws.com/weather.meersens/icons/cloudy.png",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                }
            }
        },
        {
            "found": true,
            "datetime": "2026-10-12T20:00:00.000Z",
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Correct",
                "icon": null,
                "color": "#44b001",
                "description": "Correct weather",
                "value": 31.95,
                "main_pollutants": [
                    "humidity"
                ]
            },
            "parameters": {
                "apparent_temperature": {
                    "shortcode": "aT",
                    "name": "Apparent temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.39,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "No adverse effects expected with right outfits and/or equipment",
                        "value": 3.15
                    }
                },
                "cloud_cover": {
                    "shortcode": "CC",
                    "name": "Cloud cover",
                    "found": true,
                    "confidence": 4.5,
                    "value": 90,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "humidity": {
                    "shortcode": "rH",
                    "name": "Humidity",
                    "found": true,
                    "confidence": 4.5,
                    "value": 97.37,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Correct",
                        "icon": null,
                        "color": "#44b001",
                        "description": "Wet atmosphere",
                        "value": 31.95
                    }
                },
                "precipitations": {
                    "shortcode": "Pc",
                    "name": "Precipitations",
                    "found": true,
                    "confidence": 4.5,
                    "unit": "mm",
                    "value": 0,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "No precipitation",
                        "value": 5
                    }
                },
                "pressure": {
                    "shortcode": "P",
                    "name": "Pressure",
                    "found": true,
                    "confidence": 4.5,
                    "value": 1000.84,
                    "unit": "hPa",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Depression: unsettled weather",
                        "value": 4.68
                    }
                },
                "temperature": {
                    "shortcode": "T",
                    "name": "Temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.39,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Low",
                        "icon": null,
                        "color": "#029a8d",
                        "description": "Chilly temperature",
                        "value": 21.64
                    }
                },
                "wind_direction": {
                    "shortcode": "Wd",
                    "name": "Wind direction",
                    "found": true,
                    "confidence": 4.5,
                    "value": -0.04,
                    "unit": "°",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "wind_speed": {
                    "shortcode": "Ws",
                    "name": "Wind speed",
                    "found": true,
                    "confidence": 4.5,
                    "value": 13.41,
                    "unit": "km/h",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "Light to moderate breezes",
                        "value": 12.84
                    }
                },
                "ww": {
                    "shortcode": "WW",
                    "name": "Significant weather",
                    "found": true,
                    "confidence": 4.5,
                    "qualification": "Cloudy",
                    "description": "Clouds generally forming or developing",
                    "icon": "https://s3.eu-west-2.amazonaws.com/weather.meersens/icons/cloudy.png",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                }
            }
        },
        {
            "found": true,
            "datetime": "2026-10-12T21:00:00.000Z",
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Correct",
                "icon": null,
                "color": "#44b001",
                "description": "Correct weather",
                "value": 32.04,
                "main_pollutants": [
                    "humidity"
                ]
            },
            "parameters": {
                "apparent_temperature": {
                    "shortcode": "aT",
                    "name": "Apparent temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.4,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "No adverse effects expected with right outfits and/or equipment",
                        "value": 3.15
                    }
                },
                "cloud_cover": {
                    "shortcode": "CC",
                    "name": "Cloud cover",
                    "found": true,
                    "confidence": 4.5,
                    "value": 88,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "humidity": {
                    "shortcode": "rH",
                    "name": "Humidity",
                    "found": true,
                    "confidence": 4.5,
                    "value": 97.61,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Correct",
                        "icon": null,
                        "color": "#44b001",
                        "description": "Wet atmosphere",
                        "value": 32.04
                    }
                },
                "precipitations": {
                    "shortcode": "Pc",
                    "name": "Precipitations",
                    "found": true,
                    "confidence": 4.5,
                    "unit": "mm",
                    "value": 0,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "No precipitation",
                        "value": 5
                    }
                },
                "pressure": {
                    "shortcode": "P",
                    "name": "Pressure",
                    "found": true,
                    "confidence": 4.5,
                    "value": 1001.36,
                    "unit": "hPa",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Depression: unsettled weather",
                        "value": 4.48
                    }
                },
                "temperature": {
                    "shortcode": "T",
                    "name": "Temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.4,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Low",
                        "icon": null,
                        "color": "#029a8d",
                        "description": "Chilly temperature",
                        "value": 21.62
                    }
                },
                "wind_direction": {
                    "shortcode": "Wd",
                    "name": "Wind direction",
                    "found": true,
                    "confidence": 4.5,
                    "value": -1.2,
                    "unit": "°",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "wind_speed": {
                    "shortcode": "Ws",
                    "name": "Wind speed",
                    "found": true,
                    "confidence": 4.5,
                    "value": 12.12,
                    "unit": "km/h",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "Light to moderate breezes",
                        "value": 12.02
                    }
                },
                "ww": {
                    "shortcode": "WW",
                    "name": "Significant weather",
                    "found": true,
                    "confidence": 4.5,
                    "qualification": "Cloudy",
                    "description": "Clouds generally forming or developing",
                    "icon": "https://s3.eu-west-2.amazonaws.com/weather.meersens/icons/cloudy.png",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                }
            }
        },
        {
            "found": true,
            "datetime": "2026-10-12T22:00:00.000Z",
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Correct",
                "icon": null,
                "color": "#44b001",
                "description": "Correct weather",
                "value": 31.76,
                "main_pollutants": [
                    "humidity"
                ]
            },
            "parameters": {
                "apparent_temperature": {
                    "shortcode": "aT",
                    "name": "Apparent temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.74,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "No adverse effects expected with right outfits and/or equipment",
                        "value": 3.22
                    }
                },
                "cloud_cover": {
                    "shortcode": "CC",
                    "name": "Cloud cover",
                    "found": true,
                    "confidence": 4.5,
                    "value": 88,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "humidity": {
                    "shortcode": "rH",
                    "name": "Humidity",
                    "found": true,
                    "confidence": 4.5,
                    "value": 96.89,
                    "unit": "%",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Correct",
                        "icon": null,
                        "color": "#44b001",
                        "description": "Wet atmosphere",
                        "value": 31.76
                    }
                },
                "precipitations": {
                    "shortcode": "Pc",
                    "name": "Precipitations",
                    "found": true,
                    "confidence": 4.5,
                    "unit": "mm",
                    "value": 0,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "No precipitation",
                        "value": 5
                    }
                },
                "pressure": {
                    "shortcode": "P",
                    "name": "Pressure",
                    "found": true,
                    "confidence": 4.5,
                    "value": 1001.89,
                    "unit": "hPa",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Safe",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Depression: unsettled weather",
                        "value": 4.27
                    }
                },
                "temperature": {
                    "shortcode": "T",
                    "name": "Temperature",
                    "found": true,
                    "confidence": 4.5,
                    "value": 16.74,
                    "unit": "°C",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Low",
                        "icon": null,
                        "color": "#029a8d",
                        "description": "Chilly temperature",
                        "value": 21.02
                    }
                },
                "wind_direction": {
                    "shortcode": "Wd",
                    "name": "Wind direction",
                    "found": true,
                    "confidence": 4.5,
                    "value": 12,
                    "unit": "°",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "wind_speed": {
                    "shortcode": "Ws",
                    "name": "Wind speed",
                    "found": true,
                    "confidence": 4.5,
                    "value": 10.61,
                    "unit": "km/h",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#6cd2c9",
                        "description": "Light to moderate breezes",
                        "value": 11.07
                    }
                },
                "ww": {
                    "shortcode": "WW",
                    "name": "Significant weather",
                    "found": true,
                    "confidence": 4.5,
                    "qualification": "Cloudy",
                    "description": "Clouds generally forming or developing",
                    "icon": "https://s3.eu-west-2.amazonaws.com/weather.meersens/icons/cloudy.png",
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                }
            }
        }
    ],
    "page": {
        "totalElements": 24,
        "totalPages": 4,
        "pageNumber": 1,
        "size": 6
    }
}
'''

# Metadados de EXEMPLO FIXO
metadata = {
    "contract_version": "1.0",
    "source": {"type": "api", "provider": "meersens"},
    "ingestion_datetime": "2026-10-14T18:22:00Z",
    "station": {
        "code": "FR_PARIS_488566_23522",
        "name": "Estação Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
    },
}

# Chamada para método de Construção dos documentos bronze para parâmetros de clima
document = build_bronze_documents_weather(meersens_json, metadata, allowed_parameters)
# Impressão do documento bronze construído usando dump JSON para melhor visualização na tela
print(json.dumps(document, indent=2, ensure_ascii=False))