"""Constantes do projeto - mapeamentos e configurações globais."""

# Mapeamento de códigos da API para códigos internos
# API retorna em snake_case, convertemos para UPPERCASE
WEATHER_PARAMETERS = {
    "temperature": "TEMPERATURE",
    "humidity": "HUMIDITY",
    "pressure": "PRESSURE",
    "wind_speed": "WIND_SPEED",
    "wind_direction": "WIND_DIRECTION",
    "cloud_cover": "CLOUD_COVER",
    "precipitations": "PRECIPITATIONS",
    "apparent_temperature": "APPARENT_TEMPERATURE",
}

# Unidades padrão para cada parâmetro
PARAMETER_UNITS = {
    "TEMPERATURE": "°C",
    "HUMIDITY": "%",
    "PRESSURE": "hPa",
    "WIND_SPEED": "km/h",
    "WIND_DIRECTION": "°",
    "CLOUD_COVER": "%",
    "PRECIPITATIONS": "mm",
    "APPARENT_TEMPERATURE": "°C",
}

# Parâmetros reservados (não processados agora)
RESERVED_PARAMETERS = {
    "ph": "PH",  # qualidade da água, futuro
}

# Campos da API a ignorar (não são parâmetros)
IGNORED_API_FIELDS = {
    "ww",  # código meteorológico
    "index",
    "description",
    "icon",
    "color",
    "qualification",
    "main_pollutants",
}
