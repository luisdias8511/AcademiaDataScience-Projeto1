"""Constantes do projeto - mapeamentos e configurações globais."""

# Strings de cada serviço
SERVICES = {
    "water": {
        "api_url_env": "API_URL_WATER",
        "category_code": "WATER",
        "operator_code": "OP_SERVICE_MEERSENS",
        "blob_container": "water",
        "specifications_name": "pollutants",
    },
    "weather": {
        "api_url_env": "API_URL_TEMP",
        "category_code": "WEATHER",
        "operator_code": "OP_SERVICE_MEERSENS",
        "blob_container": "weather",
        "specifications_name": "parameters",
    },
}