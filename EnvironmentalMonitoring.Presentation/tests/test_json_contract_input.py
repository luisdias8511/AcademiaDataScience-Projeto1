"""Testes isolados de entrada JSON e sua auditoria, sem Azure."""
import importlib.util
import json
import logging
from pathlib import Path
from unittest.mock import Mock

import pytest
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name + "_json_test", ROOT / f"src/processing/{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


VALIDATOR = module("bronze_contract_validator")
AUDIT = module("contract_audit")
STORAGE = module("contract_audit_storage")


def example(category):
    text = (ROOT / f"contracts/examples/{category}-bronze-valid.json").read_text(encoding="utf-8")
    schema = json.loads((ROOT / f"contracts/schemas/{category}-bronze.schema.json").read_text(encoding="utf-8"))
    return text, schema


@pytest.mark.parametrize("category", ["water", "weather"])
def test_valid_text(category):
    text, schema = example(category)
    approved, document, error = VALIDATOR.validate_json_contract(text, schema)
    assert approved is True
    assert document == json.loads(text)
    assert error is None


@pytest.mark.parametrize("text,rule", [
    ('{"value": 7 "unit": "pH"}', "json_syntax"),
    ('', "json_syntax"),
    ('{"value": 7,}', "json_syntax"),
    ('{"value": 7, "value": 8}', "json_duplicate_field"),
    ('{"value": NaN}', "json_nonfinite_number"),
    ('{"value": Infinity}', "json_nonfinite_number"),
    ('{"value": -Infinity}', "json_nonfinite_number"),
    ('{"value": 1e400}', "json_nonfinite_number"),
    ('[]', "json_root_type"),
    ('null', "json_root_type"),
])
def test_rejected_json(text, rule):
    _, schema = example("water")
    approved, document, error = VALIDATOR.validate_json_contract(text, schema)
    assert approved is False
    assert document is None
    assert error.errors[0].validator == rule


def test_valid_json_but_invalid_contract_rejects_entire_reading():
    text, schema = example("water")
    item = json.loads(text)
    item["payload"]["pollutants"][0]["value"] = "invalid"
    approved, document, error = VALIDATOR.validate_json_contract(json.dumps(item), schema)
    assert approved is False
    assert document is None
    assert any(e.validator == "type" for e in error.errors)


def test_invalid_schema_propagates():
    with pytest.raises(SchemaError):
        VALIDATOR.validate_json_contract('{}', {"type": "unknown"})


def test_wrong_input_type_is_programming_error():
    with pytest.raises(TypeError):
        VALIDATOR.validate_json_contract({}, {})


def test_malformed_json_rejection_reaches_simulated_storage():
    _, schema = example("water")
    text = '{"value": "SECRET_EXAMPLE" "other": 1}'
    approved, document, error = VALIDATOR.validate_json_contract(text, schema)
    assert approved is False and document is None
    events = AUDIT.build_contract_audit_events(
        {}, error.errors, execution_id="run-json-test", document_id="source-record-001",
        category="water", schema_name="water-bronze.schema.json",
    )
    logger = Mock(spec=logging.Logger)
    storage = Mock(spec=["upload_json"])
    AUDIT.log_contract_audit_events(events, logger)
    paths = STORAGE.save_contract_audit_events(events, storage, logger)
    assert len(paths) == 1
    assert events[0]["error_code"] == "JSON_INVALID_SYNTAX"
    assert events[0]["station_code"] is None
    assert "SECRET_EXAMPLE" not in json.dumps(events)
    storage.upload_json.assert_called_once_with(paths[0], events[0])
    logger.warning.assert_called_once()
