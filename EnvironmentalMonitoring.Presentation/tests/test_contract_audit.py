"""Testes isolados da criação e emissão dos eventos de auditoria."""
import importlib.util
import json
import logging
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "contract_audit_under_test", ROOT / "src/processing/contract_audit.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def build(document, schema, **kwargs):
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document))
    context = dict(execution_id="run-001", document_id="doc-001", category="water", schema_name="water-bronze.schema.json")
    context.update(kwargs)
    return MODULE.build_contract_audit_events(document, errors, **context)


def test_valid_document_has_no_rejection_events():
    assert build({"value": 7}, {"type": "object"}) == []


def test_multiple_failures_share_document_and_do_not_expose_values():
    document = {"value": "SEGREDO_EXEMPLO"}
    original = deepcopy(document)
    events = build(document, {"type": "object", "required": ["station"], "properties": {"value": {"type": "number"}}})
    assert len(events) == 2
    assert len({event["event_id"] for event in events}) == 2
    assert all(event["document_id"] == "doc-001" for event in events)
    assert all(event["action"] == "REJECT_DOCUMENT" for event in events)
    assert "SEGREDO_EXEMPLO" not in json.dumps(events)
    assert document == original
    required = next(event for event in events if event["rule"] == "required")
    assert required["missing_fields"] == ["station"]


def test_invalid_metadata_does_not_break_audit():
    events = build({"metadata": []}, {"properties": {"metadata": {"type": "object"}}})
    assert events[0]["station_code"] is None
    assert events[0]["contract_version"] is None


def test_real_document_context_and_field_path():
    document = json.loads((ROOT / "contracts/examples/water-bronze-valid.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "contracts/schemas/water-bronze.schema.json").read_text(encoding="utf-8"))
    document["payload"]["pollutants"][0]["value"] = "invalid"
    event = build(document, schema)[0]
    assert event["field_path"] == "/payload/pollutants/0/value"
    assert event["station_code"] == document["metadata"]["station"]["code"]
    assert event["error_code"] == "CONTRACT_INVALID_TYPE"


def test_timezone_converted_to_utc():
    moment = datetime(2026, 10, 16, 18, tzinfo=timezone(timedelta(hours=-3)))
    event = build({}, {"required": ["x"]}, occurred_at=moment)[0]
    assert event["timestamp"] == "2026-10-16T21:00:00+00:00"


def test_naive_datetime_rejected():
    with pytest.raises(ValueError, match="fuso"):
        build({}, {"required": ["x"]}, occurred_at=datetime(2026, 10, 16))


def test_datetime_error_code():
    event = build({"date": "invalid"}, {"properties": {"date": {"format": "date-time"}}})[0]
    assert event["error_code"] == "CONTRACT_INVALID_DATETIME"


def test_logger_receives_event_without_reserved_message():
    events = build({}, {"required": ["x"]})
    logger = Mock(spec=logging.Logger)
    MODULE.log_contract_audit_events(events, logger)
    logger.warning.assert_called_once()
    extra = logger.warning.call_args.kwargs["extra"]
    assert "message" not in extra
    assert extra["event_timestamp"] == events[0]["timestamp"]
    assert extra["event_id"] == events[0]["event_id"]
