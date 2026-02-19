import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from embedm.domain.directive import Directive
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm_plugins.table_plugin import TablePlugin
from embedm_plugins.table_transformer import FILTER_KEY, LIMIT_KEY, MAX_CELL_LENGTH_KEY


def _make_cache(tmp_path: Path) -> FileCache:
    return FileCache(max_file_size=1024 * 1024, memory_limit=10 * 1024 * 1024, allowed_paths=[str(tmp_path)])


def _make_plan_node(source: str, options: dict[str, str] | None = None) -> PlanNode:
    directive = Directive(type="table", source=source, options=options or {})
    document = MagicMock()
    return PlanNode(directive=directive, status=[], document=document)


# --- validate_directive ---


def test_validate_missing_source():
    plugin = TablePlugin()
    errors = plugin.validate_directive(Directive(type="table"))
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "source" in errors[0].description


def test_validate_unsupported_extension():
    plugin = TablePlugin()
    errors = plugin.validate_directive(Directive(type="table", source="data.xlsx"))
    assert any("xlsx" in e.description for e in errors)


def test_validate_invalid_limit():
    plugin = TablePlugin()
    errors = plugin.validate_directive(Directive(type="table", source="data.csv", options={LIMIT_KEY: "abc"}))
    assert any(e.level == StatusLevel.ERROR for e in errors)


def test_validate_invalid_filter_not_dict():
    plugin = TablePlugin()
    errors = plugin.validate_directive(
        Directive(type="table", source="data.csv", options={FILTER_KEY: json.dumps([1, 2])})
    )
    assert any("filter" in e.description for e in errors)


def test_validate_invalid_filter_bad_json():
    plugin = TablePlugin()
    errors = plugin.validate_directive(
        Directive(type="table", source="data.csv", options={FILTER_KEY: "not_json"})
    )
    assert any("filter" in e.description for e in errors)


def test_validate_valid_csv():
    plugin = TablePlugin()
    errors = plugin.validate_directive(Directive(type="table", source="/some/path/data.csv"))
    assert errors == []


def test_validate_valid_json():
    plugin = TablePlugin()
    errors = plugin.validate_directive(Directive(type="table", source="/some/path/data.json"))
    assert errors == []


def test_validate_valid_tsv():
    plugin = TablePlugin()
    errors = plugin.validate_directive(Directive(type="table", source="/some/path/data.tsv"))
    assert errors == []


def test_validate_valid_with_all_options():
    plugin = TablePlugin()
    options = {
        LIMIT_KEY: "10",
        MAX_CELL_LENGTH_KEY: "80",
        FILTER_KEY: json.dumps({"col": "value"}),
    }
    errors = plugin.validate_directive(Directive(type="table", source="/path/data.csv", options=options))
    assert errors == []


# --- transform ---


def test_transform_no_document():
    plugin = TablePlugin()
    plan_node = PlanNode(Directive(type="table", source="data.csv"), status=[], document=None)
    result = plugin.transform(plan_node, [], MagicMock())
    assert result == ""


def test_transform_csv(tmp_path: Path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,score\nAlice,90\nBob,80\n")

    plugin = TablePlugin()
    plan_node = _make_plan_node(str(csv_file))
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "| name | score |" in result
    assert "| Alice | 90 |" in result
    assert "| Bob | 80 |" in result


def test_transform_json(tmp_path: Path):
    json_file = tmp_path / "data.json"
    json_file.write_text('[{"city": "Paris", "pop": 2161000}]')

    plugin = TablePlugin()
    plan_node = _make_plan_node(str(json_file))
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "| city | pop |" in result
    assert "Paris" in result


def test_transform_tsv(tmp_path: Path):
    tsv_file = tmp_path / "data.tsv"
    tsv_file.write_text("col1\tcol2\nfoo\tbar\n")

    plugin = TablePlugin()
    plan_node = _make_plan_node(str(tsv_file))
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "| col1 | col2 |" in result
    assert "foo" in result


def test_transform_with_select(tmp_path: Path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,score,grade\nAlice,90,A\n")

    plugin = TablePlugin()
    plan_node = _make_plan_node(str(csv_file), options={"select": "name, grade as g"})
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "| name | g |" in result
    assert "score" not in result


def test_transform_with_filter(tmp_path: Path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,score\nAlice,90\nBob,50\n")

    plugin = TablePlugin()
    plan_node = _make_plan_node(str(csv_file), options={FILTER_KEY: json.dumps({"score": ">= 80"})})
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "Alice" in result
    assert "Bob" not in result
