"""Testes isolados: não carregam os serviços externos importados por src."""
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "bronze_contract_validator_under_test",
    ROOT / "src/processing/bronze_contract_validator.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
validate_contract = MODULE.validate_contract
ContractValidationError = MODULE.ContractValidationError


def load(category):
    schema = json.loads((ROOT / f"contracts/schemas/{category}-bronze.schema.json").read_text(encoding="utf-8"))
    document = json.loads((ROOT / f"contracts/examples/{category}-bronze-valid.json").read_text(encoding="utf-8"))
    return document, schema


@pytest.mark.parametrize("category", ["weather", "water"])
def test_valid_examples(category):
    document, schema = load(category)
    assert validate_contract(document, schema) == (True, None)


def test_multiple_errors_and_original_preserved():
    document, schema = load("water")
    del document["metadata"]["station"]
    document["payload"]["pollutants"][0]["value"] = "invalid"
    original = deepcopy(document)
    approved, error = validate_contract(document, schema)
    assert approved is False
    assert isinstance(error, ContractValidationError)
    assert len(error.errors) == 2
    assert {e.validator for e in error.errors} == {"required", "type"}
    assert document == original


@pytest.mark.parametrize("timestamp", ["invalid", "2026-10-14T00:00:00"])
def test_invalid_datetime(timestamp):
    document, schema = load("weather")
    document["payload"]["datetime"] = timestamp
    approved, error = validate_contract(document, schema)
    assert approved is False
    assert any(e.validator == "format" for e in error.errors)


def test_empty_measurements():
    document, schema = load("water")
    document["payload"]["pollutants"] = []
    approved, error = validate_contract(document, schema)
    assert approved is False
    assert error.errors[0].validator == "minItems"


def test_invalid_schema_is_operational_failure():
    with pytest.raises(SchemaError):
        validate_contract({}, {"type": "unknown_type"})
