import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.bronze_contract_validator import validate_contract


BASE_DIR = Path(__file__).parent.parent
EXAMPLE_DOCUMENT_PATH = BASE_DIR / "examples" / "weather-bronze.document.json"
SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "weather-bronze.schema.json"


with EXAMPLE_DOCUMENT_PATH.open("r", encoding="utf-8") as document_file:
    bronze_document = json.load(document_file)

with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
    weather_schema = json.load(schema_file)

is_valid, error = validate_contract(bronze_document, weather_schema)
print(f"Validação de contrato: {is_valid}")
if error:
    print(f"Erro: {error}")
