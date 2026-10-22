"""Conversão e leitura do Parquet real, sem acesso ao Azure."""
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "json_to_parquet_under_test", ROOT / "src/processing/json_to_parquet.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def read(content):
    return pq.ParquetFile(pa.BufferReader(content)).read()


@pytest.mark.parametrize("category", ["water", "weather"])
def test_bronze_document_preserves_nested_content(category):
    text = (ROOT / f"contracts/examples/{category}-bronze-valid.json").read_text(encoding="utf-8")
    original = json.loads(text)
    before = deepcopy(original)
    content = MODULE.json_to_parquet(original)
    assert isinstance(content, bytes)
    assert content[:4] == b"PAR1" and content[-4:] == b"PAR1"
    assert read(content).to_pylist() == [original]
    assert original == before
    metadata = pq.ParquetFile(pa.BufferReader(content)).metadata
    for row in range(metadata.num_row_groups):
        for column in range(metadata.num_columns):
            assert metadata.row_group(row).column(column).compression == "SNAPPY"


@pytest.mark.parametrize("encoding", ["text", "bytes"])
def test_serialized_json_list(encoding):
    records = [{"station": "EST_001", "value": 7.2}, {"station": "EST_002", "value": 8.0}]
    source = json.dumps(records)
    if encoding == "bytes":
        source = source.encode("utf-8")
    assert read(MODULE.json_to_parquet(source)).to_pylist() == records


def test_optional_fields_in_later_rows_are_preserved():
    source = [{"value": 1}, {"value": 2, "unit": "°C"}]
    assert read(MODULE.json_to_parquet(source)).to_pylist() == [
        {"value": 1, "unit": None}, {"value": 2, "unit": "°C"}
    ]


def test_empty_list_produces_readable_parquet():
    assert read(MODULE.json_to_parquet([])).num_rows == 0


def test_conversion_does_not_apply_quality_rules():
    assert read(MODULE.json_to_parquet({"parameter_code": "PH", "value": 18})).to_pylist()[0]["value"] == 18
