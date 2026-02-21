import json
from pathlib import Path
from unittest.mock import MagicMock

from embedm.domain.directive import Directive
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm_plugins.plugin_resources import str_resources
from embedm_plugins.table_plugin import TablePlugin
from embedm_plugins.table_transformer import FILTER_KEY, LIMIT_KEY, MAX_CELL_LENGTH_KEY

Row = dict[str, str]


def _make_cache(tmp_path: Path) -> FileCache:
    return FileCache(max_file_size=1024 * 1024, memory_limit=10 * 1024 * 1024, allowed_paths=[str(tmp_path)])


def _make_plan_node(source: str, options: dict[str, str] | None = None, artifact: object = None) -> PlanNode:
    directive = Directive(type="table", source=source, options=options or {})
    document = MagicMock()
    node = PlanNode(directive=directive, status=[], document=document)
    node.artifact = artifact
    return node


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


# --- validate_input ---


def test_validate_input_csv_returns_rows_as_artifact():
    plugin = TablePlugin()
    directive = Directive(type="table", source="/path/data.csv")
    result = plugin.validate_input(directive, "name,age\nAlice,30\nBob,25\n")
    assert result.errors == []
    assert result.artifact == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]


def test_validate_input_tsv_returns_rows_as_artifact():
    plugin = TablePlugin()
    directive = Directive(type="table", source="/path/data.tsv")
    result = plugin.validate_input(directive, "name\tage\nAlice\t30\n")
    assert result.errors == []
    assert result.artifact == [{"name": "Alice", "age": "30"}]


def test_validate_input_json_returns_rows_as_artifact():
    plugin = TablePlugin()
    directive = Directive(type="table", source="/path/data.json")
    result = plugin.validate_input(directive, '[{"city": "Paris", "pop": "2000"}]')
    assert result.errors == []
    assert result.artifact == [{"city": "Paris", "pop": "2000"}]


def test_validate_input_empty_csv_returns_error():
    plugin = TablePlugin()
    directive = Directive(type="table", source="/path/data.csv")
    result = plugin.validate_input(directive, "name,age\n")
    assert len(result.errors) == 1
    assert result.errors[0].level == StatusLevel.ERROR
    assert result.artifact is None


def test_validate_input_invalid_json_returns_error():
    plugin = TablePlugin()
    directive = Directive(type="table", source="/path/data.json")
    result = plugin.validate_input(directive, "not json")
    assert any(e.level == StatusLevel.ERROR for e in result.errors)
    assert result.artifact is None


def test_validate_input_unknown_select_column_returns_error():
    plugin = TablePlugin()
    directive = Directive(type="table", source="/path/data.csv", options={"select": "missing"})
    result = plugin.validate_input(directive, "name,age\nAlice,30\n")
    assert any("missing" in e.description for e in result.errors)
    assert result.artifact is None


def test_validate_input_invalid_order_by_returns_error():
    plugin = TablePlugin()
    directive = Directive(type="table", source="/path/data.csv", options={"order_by": "col a b"})
    result = plugin.validate_input(directive, "name,age\nAlice,30\n")
    assert any(e.level == StatusLevel.ERROR for e in result.errors)
    assert result.artifact is None


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
    rows: list[Row] = [{"name": "Alice", "score": "90"}, {"name": "Bob", "score": "80"}]
    plan_node = _make_plan_node(str(csv_file), artifact=rows)
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "| name | score |" in result
    assert "| Alice | 90 |" in result
    assert "| Bob | 80 |" in result


def test_transform_json(tmp_path: Path):
    json_file = tmp_path / "data.json"
    json_file.write_text('[{"city": "Paris", "pop": "2161000"}]')

    plugin = TablePlugin()
    rows: list[Row] = [{"city": "Paris", "pop": "2161000"}]
    plan_node = _make_plan_node(str(json_file), artifact=rows)
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "| city | pop |" in result
    assert "Paris" in result


def test_transform_with_select(tmp_path: Path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,score,grade\nAlice,90,A\n")

    plugin = TablePlugin()
    rows: list[Row] = [{"name": "Alice", "score": "90", "grade": "A"}]
    plan_node = _make_plan_node(str(csv_file), options={"select": "name, grade as g"}, artifact=rows)
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "| name | g |" in result
    assert "score" not in result


def test_transform_with_filter(tmp_path: Path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,score\nAlice,90\nBob,50\n")

    plugin = TablePlugin()
    rows: list[Row] = [{"name": "Alice", "score": "90"}, {"name": "Bob", "score": "50"}]
    plan_node = _make_plan_node(str(csv_file), options={FILTER_KEY: json.dumps({"score": ">= 80"})}, artifact=rows)
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)

    assert "Alice" in result
    assert "Bob" not in result


def test_transform_no_artifact_returns_no_results(tmp_path: Path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAlice,30\n")

    plugin = TablePlugin()
    plan_node = _make_plan_node(str(csv_file), artifact=None)
    cache = _make_cache(tmp_path)

    result = plugin.transform(plan_node, [], cache)
    assert str_resources.note_no_results in result
