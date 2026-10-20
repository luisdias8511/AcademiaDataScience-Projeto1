"""Regras de qualidade, limites configuráveis e auditoria simulada."""
import importlib.util
import json
import logging
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name + "_quality_test", ROOT / f"src/processing/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DQ = load_module("data_quality")
AUDIT = load_module("contract_audit")
STORAGE = load_module("contract_audit_storage")


def example(category="water"):
    return json.loads((ROOT / f"contracts/examples/{category}-bronze-valid.json").read_text(encoding="utf-8"))


def ph_document(value=7):
    doc = example()
    item = next(item for item in doc["payload"]["pollutants"] if item["parameter_code"] == "PH")
    item["value"] = value
    doc["payload"]["pollutants"] = [item]
    return doc


@pytest.mark.parametrize("category", ["water", "weather"])
def test_examples_approved_without_mutation(category):
    doc = example(category)
    original = deepcopy(doc)
    report = DQ.assess_data_quality([doc], category)
    assert report["summary"]["approved_documents"] == 1
    assert doc == original
    assert report["results"][0]["unchecked_rules"]


@pytest.mark.parametrize("value", [0, 14, 7.2])
def test_ph_inclusive_bounds(value):
    assert DQ.assess_data_quality([ph_document(value)], "water")["results"][0]["approved"]


@pytest.mark.parametrize("value", [-0.1, 14.1])
def test_invalid_ph_rejects_full_document(value):
    doc = example()
    next(item for item in doc["payload"]["pollutants"] if item["parameter_code"] == "PH")["value"] = value
    result = DQ.assess_data_quality([doc], "water")["results"][0]
    assert not result["approved"]
    assert result["action"] == "REJECT_DOCUMENT"
    assert result["errors"][0]["error_code"] == "DQ_OUT_OF_RANGE"
    assert len(doc["payload"]["pollutants"]) == 5


@pytest.mark.parametrize("value", [True, "7", float("nan"), float("inf")])
def test_invalid_numbers(value):
    result = DQ.assess_data_quality([ph_document(value)], "water")["results"][0]
    assert result["errors"][0]["error_code"] == "DQ_INVALID_NUMBER"


def test_unit_mismatch():
    doc = ph_document()
    doc["payload"]["pollutants"][0]["unit"] = "other"
    result = DQ.assess_data_quality([doc], "water")["results"][0]
    assert result["errors"][0]["error_code"] == "DQ_UNIT_MISMATCH"


@pytest.mark.parametrize("code", ["UNKNOWN", "AIR_TEMPERATURE"])
def test_parameter_not_allowed_in_water(code):
    doc = ph_document()
    doc["payload"]["pollutants"][0]["parameter_code"] = code
    assert not DQ.assess_data_quality([doc], "water")["results"][0]["approved"]


def test_identical_duplicate():
    report = DQ.assess_data_quality([ph_document(), ph_document()], "water")
    assert report["summary"]["approved_documents"] == 1
    assert report["summary"]["rejected_documents"] == 1
    assert report["results"][1]["errors"][0]["error_code"] == "DQ_DUPLICATE_MEASUREMENT"


def test_conflicting_duplicate():
    report = DQ.assess_data_quality([ph_document(7), ph_document(8)], "water")
    assert report["results"][1]["errors"][0]["error_code"] == "DQ_CONFLICTING_MEASUREMENT"


def test_rejected_document_does_not_reserve_keys():
    bad = example()
    next(item for item in bad["payload"]["pollutants"] if item["parameter_code"] == "PH")["value"] = 18
    report = DQ.assess_data_quality([bad, example()], "water")
    assert not report["results"][0]["approved"]
    assert report["results"][1]["approved"]


def test_duplicate_inside_document():
    doc = ph_document()
    doc["payload"]["pollutants"].append(deepcopy(doc["payload"]["pollutants"][0]))
    assert not DQ.assess_data_quality([doc], "water")["results"][0]["approved"]


def test_same_instant_different_timezone_is_duplicate():
    first, second = ph_document(), ph_document()
    first["payload"]["datetime"] = "2026-10-14T00:00:00Z"
    second["payload"]["datetime"] = "2026-10-13T21:00:00-03:00"
    assert not DQ.assess_data_quality([first, second], "water")["results"][1]["approved"]


def test_future_unconfigured_warns():
    doc = ph_document()
    doc["payload"]["datetime"] = "2026-10-15T00:00:00Z"
    result = DQ.assess_data_quality([doc], "water", future_tolerance=None)["results"][0]
    assert result["approved"]
    assert result["warnings"][0]["error_code"] == "DQ_FUTURE_READING"


def test_future_tolerance_rejects():
    doc = ph_document()
    doc["payload"]["datetime"] = "2026-10-15T00:00:00Z"
    assert not DQ.assess_data_quality([doc], "water", future_tolerance=timedelta(minutes=5))["results"][0]["approved"]


def test_delay_only_warns_in_realtime():
    kwargs = dict(maximum_delay=timedelta(hours=1))
    historical = DQ.assess_data_quality([ph_document()], "water", **kwargs)
    realtime = DQ.assess_data_quality([ph_document()], "water", mode="realtime", **kwargs)
    assert historical["results"][0]["warnings"] == []
    assert realtime["results"][0]["approved"]
    assert realtime["results"][0]["warnings"][0]["error_code"] == "DQ_DELAYED_READING"


def test_custom_bounds_without_mutating_defaults():
    rules = deepcopy(DQ.PARAMETER_RULES)
    rules["AIR_TEMPERATURE"]["maximum"] = 10
    report = DQ.assess_data_quality([example("weather")], "weather", rules=rules)
    assert not report["results"][0]["approved"]
    assert DQ.PARAMETER_RULES["AIR_TEMPERATURE"]["maximum"] is None


def test_invalid_config_fails():
    rules = deepcopy(DQ.PARAMETER_RULES)
    rules["PH"]["minimum"] = 20
    with pytest.raises(ValueError):
        DQ.assess_data_quality([], "water", rules=rules)


def test_empty_batch():
    assert DQ.assess_data_quality([], "water")["summary"]["received_documents"] == 0


def test_quality_rejection_audit_and_simulated_storage():
    doc = ph_document(18)
    result = DQ.assess_data_quality([doc], "water")["results"][0]
    events = DQ.build_data_quality_audit_events(doc, result, execution_id="quality-run", document_id="doc-001", category="water")
    assert events[0]["event_type"] == "DATA_QUALITY_VALIDATION_FAILED"
    logger = Mock(spec=logging.Logger)
    storage = Mock(spec=["upload_json"])
    AUDIT.log_contract_audit_events(events, logger)
    paths = STORAGE.save_contract_audit_events(events, storage, logger)
    assert paths[0].startswith("quality-rejections/")
    storage.upload_json.assert_called_once()
    logger.warning.assert_called_once()


def test_approved_result_has_no_rejection_events():
    doc = ph_document()
    result = DQ.assess_data_quality([doc], "water")["results"][0]
    assert DQ.build_data_quality_audit_events(doc, result, execution_id="run", document_id="doc", category="water") == []


@pytest.mark.parametrize("code", ["CONDUCTIVITY", "HARDNESS", "TURBIDITY"])
@pytest.mark.parametrize("value,approved", [(-0.01, False), (0, True)])
def test_nonnegative_parameter_bounds(code, value, approved):
    doc = example()
    item = next(item for item in doc["payload"]["pollutants"] if item["parameter_code"] == code)
    item["value"] = value
    result = DQ.assess_data_quality([doc], "water")["results"][0]
    assert result["approved"] is approved
    if not approved:
        assert result["action"] == "REJECT_DOCUMENT"
        assert any(error["error_code"] == "DQ_OUT_OF_RANGE" for error in result["errors"])


@pytest.mark.parametrize("seconds,approved", [(0, True), (299, True), (300, True), (301, False), (600, False)])
def test_default_future_tolerance_boundary(seconds, approved):
    from datetime import datetime
    doc = ph_document()
    ingestion = datetime.fromisoformat(doc["metadata"]["ingestion_datetime"].replace("Z", "+00:00"))
    doc["payload"]["datetime"] = (ingestion + timedelta(seconds=seconds)).isoformat()
    result = DQ.assess_data_quality([doc], "water")["results"][0]
    assert result["approved"] is approved
    assert result["warnings"] == []
    assert "future_tolerance_not_configured" not in result["unchecked_rules"]


@pytest.mark.parametrize("seconds,warns", [(3600, False), (3601, True)])
def test_configured_delay_boundary_is_only_warning(seconds, warns):
    from datetime import datetime
    doc = ph_document()
    ingestion = datetime.fromisoformat(doc["metadata"]["ingestion_datetime"].replace("Z", "+00:00"))
    doc["payload"]["datetime"] = (ingestion - timedelta(seconds=seconds)).isoformat()
    result = DQ.assess_data_quality([doc], "water", mode="realtime", maximum_delay=timedelta(hours=1))["results"][0]
    assert result["approved"]
    assert bool(result["warnings"]) is warns


def test_pending_bounds_remain_explicit():
    result = DQ.assess_data_quality([example()], "water")["results"][0]
    assert "CONDUCTIVITY.maximum_not_configured" in result["unchecked_rules"]
    assert "CONDUCTIVITY.minimum_not_configured" not in result["unchecked_rules"]
    assert "WATER_TEMPERATURE.minimum_not_configured" in result["unchecked_rules"]
    assert "WATER_TEMPERATURE.maximum_not_configured" in result["unchecked_rules"]
