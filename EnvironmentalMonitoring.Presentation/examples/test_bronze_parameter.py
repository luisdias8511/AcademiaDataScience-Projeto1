import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.bronze_parameter_validator import validate_parameter

value = 16.74

is_valid, error = validate_parameter(value)
print(f"Validação de parâmetro ({value}): {is_valid}")
if error:
    print(f"Erro: {error}")