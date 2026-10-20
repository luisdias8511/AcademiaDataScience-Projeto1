"""Testes isolados, sem credenciais e sem envio ao Azure."""
import importlib.util
import logging
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "contract_audit_storage_under_test",
    ROOT / "src/processing/contract_audit_storage.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def event(event_id="11111111-1111-4111-8111-111111111111"):
    return {
        "event_id": event_id,
        "event_type": "CONTRACT_VALIDATION_FAILED",
        "action": "REJECT_DOCUMENT",
        "execution_id": "run-001",
        "document_id": "reading-001",
        "category": "water",
        "timestamp": "2026-10-19T18:00:00+00:00",
        "error_code": "CONTRACT_INVALID_TYPE",
    }


def services():
    return Mock(spec=["upload_json"]), Mock(spec=logging.Logger)


def test_upload_preserves_content_and_returns_path():
    item = event()
    before = deepcopy(item)
    storage, logger = services()
    paths = MODULE.save_contract_audit_events([item], storage, logger)
    assert len(paths) == 1
    assert paths[0].startswith("contract-rejections/year=2026/month=10/day=19/category=water/")
    assert paths[0].endswith(item["event_id"] + ".json")
    storage.upload_json.assert_called_once_with(paths[0], item)
    logger.info.assert_called_once()
    assert item == before


def test_empty_batch_does_not_upload():
    storage, logger = services()
    assert MODULE.save_contract_audit_events([], storage, logger) == []
    storage.upload_json.assert_not_called()


def test_reusing_event_reuses_path():
    storage, logger = services()
    first = MODULE.save_contract_audit_events([event()], storage, logger)
    second = MODULE.save_contract_audit_events([event()], storage, logger)
    assert first == second


def test_distinct_events_produce_distinct_files():
    storage, logger = services()
    items = [event(), event("22222222-2222-4222-8222-222222222222")]
    paths = MODULE.save_contract_audit_events(items, storage, logger)
    assert len(set(paths)) == 2
    assert storage.upload_json.call_count == 2


def test_failure_is_logged_and_propagated():
    storage, logger = services()
    storage.upload_json.side_effect = OSError("simulated")
    with pytest.raises(MODULE.AuditPersistenceError) as captured:
        MODULE.save_contract_audit_events([event()], storage, logger)
    assert captured.value.saved_paths == ()
    logger.error.assert_called_once()
    logger.info.assert_not_called()


def test_partial_failure_reports_confirmed_paths():
    storage, logger = services()
    storage.upload_json.side_effect = [None, OSError("simulated"), None]
    items = [event(), event("22222222-2222-4222-8222-222222222222"), event("33333333-3333-4333-8333-333333333333")]
    with pytest.raises(MODULE.AuditPersistenceError) as captured:
        MODULE.save_contract_audit_events(items, storage, logger)
    assert len(captured.value.saved_paths) == 1
    assert storage.upload_json.call_count == 2


def test_invalid_later_event_prevents_all_uploads():
    storage, logger = services()
    invalid = event("not-a-uuid")
    with pytest.raises(ValueError):
        MODULE.save_contract_audit_events([event(), invalid], storage, logger)
    storage.upload_json.assert_not_called()


def test_duplicate_event_prevents_all_uploads():
    storage, logger = services()
    with pytest.raises(ValueError, match="repetidos"):
        MODULE.save_contract_audit_events([event(), event()], storage, logger)
    storage.upload_json.assert_not_called()


def test_path_uses_utc_date():
    storage, logger = services()
    item = event()
    item["timestamp"] = "2026-10-19T23:30:00-03:00"
    paths = MODULE.save_contract_audit_events([item], storage, logger)
    assert "day=20/" in paths[0]
