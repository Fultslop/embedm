import pytest

from embedm_plugins.plugin_resources import str_resources
from embedm_plugins.table_transformer import TableParams, TableTransformer


def _run(
    content: str,
    ext: str = "csv",
    select: str = "",
    order_by: str = "",
    limit: int = -1,
    offset: int = 0,
    filter_map: dict[str, str] | None = None,
    date_format: str = "",
    null_string: str = "",
    max_cell_length: int = 0,
) -> str:
    return TableTransformer().execute(
        TableParams(
            content=content,
            file_ext=ext,
            select=select,
            order_by=order_by,
            limit=limit,
            offset=offset,
            filter_map=filter_map or {},
            date_format=date_format,
            null_string=null_string,
            max_cell_length=max_cell_length,
        )
    )


_CSV = "name,age\nAlice,30\nBob,25\nCarol,35\n"
_TSV = "name\tage\nAlice\t30\nBob\t25\n"
_JSON = '[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'


# --- parsing ---


def test_parse_csv():
    result = _run(_CSV)
    assert "| name | age |" in result
    assert "| Alice | 30 |" in result
    assert "| Bob | 25 |" in result


def test_parse_tsv():
    result = _run(_TSV, ext="tsv")
    assert "| name | age |" in result
    assert "| Alice | 30 |" in result


def test_parse_json():
    result = _run(_JSON, ext="json")
    assert "| name | age |" in result
    assert "| Alice | 30 |" in result


def test_parse_json_invalid():
    result = _run("not json", ext="json")
    assert "[!CAUTION]" in result
    assert "invalid JSON" in result


def test_parse_json_not_array():
    result = _run('{"key": "val"}', ext="json")
    assert "[!CAUTION]" in result
    assert "array of objects" in result


def test_parse_json_not_objects():
    result = _run('[1, 2, 3]', ext="json")
    assert "[!CAUTION]" in result
    assert "objects" in result


def test_parse_unsupported_extension():
    result = _run("data", ext="xlsx")
    assert "[!CAUTION]" in result
    assert "xlsx" in result


def test_empty_csv():
    result = _run("name,age\n")
    assert str_resources.note_no_table_content in result


def test_empty_json():
    result = _run("[]", ext="json")
    assert str_resources.note_no_table_content in result


# --- select ---


def test_select_single_column():
    result = _run(_CSV, select="name")
    assert "| name |" in result
    assert "age" not in result


def test_select_with_alias():
    result = _run(_CSV, select="name as person")
    assert "| person |" in result
    assert "name" not in result
    assert "Alice" in result


def test_select_multiple_columns():
    result = _run(_CSV, select="age, name")
    assert result.startswith("| age | name |")


def test_select_unknown_column():
    result = _run(_CSV, select="missing")
    assert "[!CAUTION]" in result
    assert "missing" in result


def test_select_invalid_expression():
    result = _run(_CSV, select="col a b c")
    assert "[!CAUTION]" in result


# --- filter ---


def test_filter_exact_match():
    result = _run(_CSV, filter_map={"name": "Alice"})
    assert "Alice" in result
    assert "Bob" not in result


def test_filter_operator_less_than():
    result = _run(_CSV, filter_map={"age": "< 31"})
    assert "Alice" in result
    assert "Bob" in result
    assert "Carol" not in result


def test_filter_operator_greater_equal():
    result = _run(_CSV, filter_map={"age": ">= 30"})
    assert "Alice" in result
    assert "Carol" in result
    assert "Bob" not in result


def test_filter_operator_not_equal():
    result = _run(_CSV, filter_map={"name": "!= Alice"})
    assert "Alice" not in result
    assert "Bob" in result


def test_filter_removes_all_rows():
    result = _run(_CSV, filter_map={"name": "nobody"})
    assert str_resources.note_no_table_content in result


def test_filter_invalid_operator():
    result = _run(_CSV, filter_map={"age": "~~ 30"})
    # ~~ is not a valid operator, treated as exact match (no match for "~~ 30")
    # so all rows are filtered out
    assert str_resources.note_no_table_content in result


# --- order_by ---


def test_order_by_asc():
    result = _run(_CSV, order_by="name asc")
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert lines[0].startswith("| Alice")
    assert lines[1].startswith("| Bob")
    assert lines[2].startswith("| Carol")


def test_order_by_desc():
    result = _run(_CSV, order_by="name desc")
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert lines[0].startswith("| Carol")


def test_order_by_numeric():
    result = _run(_CSV, order_by="age asc")
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert lines[0].startswith("| Bob")


def test_order_by_invalid_expression():
    result = _run(_CSV, order_by="col a b")
    assert "[!CAUTION]" in result


# --- limit and offset ---


def test_limit():
    result = _run(_CSV, limit=1)
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert len(lines) == 1


def test_offset():
    result = _run(_CSV, offset=2)
    assert "Alice" not in result
    assert "Bob" not in result
    assert "Carol" in result


def test_limit_and_offset():
    result = _run(_CSV, order_by="name asc", offset=1, limit=1)
    assert "Bob" in result
    assert "Alice" not in result
    assert "Carol" not in result


def test_limit_beyond_rows():
    result = _run(_CSV, limit=100)
    assert "Alice" in result
    assert "Bob" in result


def test_offset_beyond_rows():
    result = _run(_CSV, offset=100)
    assert str_resources.note_no_table_content in result


# --- rendering options ---


def test_null_string():
    csv_data = "name,score\nAlice,\nBob,10\n"
    result = _run(csv_data, null_string="-")
    assert "| - |" in result or "| Alice | - |" in result


def test_max_cell_length_truncates():
    csv_data = "name\nAlice123456789\n"
    result = _run(csv_data, max_cell_length=5)
    assert "Alic\u2026" in result  # 4 chars + ellipsis = 5 total


def test_max_cell_length_zero_no_truncation():
    csv_data = "name\nAlice123456789\n"
    result = _run(csv_data, max_cell_length=0)
    assert "Alice123456789" in result


def test_date_format():
    csv_data = "name,created\nAlice,2024-01-15\n"
    result = _run(csv_data, date_format="%d/%m/%Y")
    assert "15/01/2024" in result


def test_date_format_non_date_unchanged():
    csv_data = "name,value\nAlice,hello\n"
    result = _run(csv_data, date_format="%Y-%m-%d")
    assert "hello" in result


def test_pipe_escaped_in_cell():
    csv_data = "name\nAlice|Bob\n"
    result = _run(csv_data)
    assert "Alice\\|Bob" in result


def test_newline_replaced_in_cell():
    csv_data = "name,score\nAlice,10\n"
    # inject a newline through JSON
    json_data = '[{"name": "Ali\\nce", "score": "10"}]'
    result = _run(json_data, ext="json")
    assert "\n" not in result.replace("\n| ", "X").split("X")[0]  # no raw newlines in cells


# --- table structure ---


def test_output_ends_with_newline():
    result = _run(_CSV)
    assert result.endswith("\n")


def test_header_separator_row():
    result = _run(_CSV)
    lines = result.splitlines()
    assert lines[1] == "| --- | --- |"


def test_json_bool_values():
    json_data = '[{"active": true, "name": "Alice"}]'
    result = _run(json_data, ext="json")
    assert "true" in result


def test_json_null_values_use_null_string():
    json_data = '[{"name": "Alice", "score": null}]'
    result = _run(json_data, ext="json", null_string="N/A")
    assert "N/A" in result
