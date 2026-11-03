"""Constantes do projeto - mapeamentos e configurações globais."""

# Strings de cada serviço
SERVICES = {
    "water": {
        "api_url_env": "API_URL_WATER",
        "category_code": "WATER",
        "operator_code": "OP_SERVICE_MEERSENS",
        "blob_container_bronze": "water",
        "blob_container_silver": "water-silver",
        "specifications_name": "pollutants",
    },
    "weather": {
        "api_url_env": "API_URL_TEMP",
        "category_code": "WEATHER",
        "operator_code": "OP_SERVICE_MEERSENS",
        "blob_container_bronze": "weather",
        "blob_container_silver": "weather-silver",
        "specifications_name": "parameters",
    },
    "audit": {
        "blob_container": "audit",
    },
}