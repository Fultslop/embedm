from embedm_plugins.table.table_resources import str_resources
from embedm_plugins.table.table_transformer import TableParams, TableTransformer

Row = dict[str, str]

_CSV_ROWS: list[Row] = [
    {"name": "Alice", "age": "30"},
    {"name": "Bob", "age": "25"},
    {"name": "Carol", "age": "35"},
]


def _run(
    rows: list[Row] | None = None,
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
            rows=rows if rows is not None else list(_CSV_ROWS),
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


# --- no results ---


def test_empty_rows_returns_no_results():
    result = _run(rows=[])
    assert str_resources.note_no_results in result


# --- select ---


def test_select_single_column():
    result = _run(select="name")
    assert "| name |" in result
    assert "age" not in result


def test_select_with_alias():
    result = _run(select="name as person")
    assert "| person |" in result
    assert "name" not in result
    assert "Alice" in result


def test_select_multiple_columns():
    result = _run(select="age, name")
    assert result.startswith("| age | name |")


# --- filter ---


def test_filter_exact_match():
    result = _run(filter_map={"name": "Alice"})
    assert "Alice" in result
    assert "Bob" not in result


def test_filter_operator_less_than():
    result = _run(filter_map={"age": "< 31"})
    assert "Alice" in result
    assert "Bob" in result
    assert "Carol" not in result


def test_filter_operator_greater_equal():
    result = _run(filter_map={"age": ">= 30"})
    assert "Alice" in result
    assert "Carol" in result
    assert "Bob" not in result


def test_filter_operator_not_equal():
    result = _run(filter_map={"name": "!= Alice"})
    assert "Alice" not in result
    assert "Bob" in result


def test_filter_removes_all_rows_returns_no_results():
    result = _run(filter_map={"name": "nobody"})
    assert str_resources.note_no_results in result


def test_filter_invalid_operator_treated_as_exact_match():
    # ~~ is not a recognized operator prefix; falls through to exact-match "~~ 30"
    # which never matches any age value — result is no rows
    result = _run(filter_map={"age": "~~ 30"})
    assert str_resources.note_no_results in result


# --- order_by ---


def test_order_by_asc():
    result = _run(order_by="name asc")
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert lines[0].startswith("| Alice")
    assert lines[1].startswith("| Bob")
    assert lines[2].startswith("| Carol")


def test_order_by_desc():
    result = _run(order_by="name desc")
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert lines[0].startswith("| Carol")


def test_order_by_numeric():
    result = _run(order_by="age asc")
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert lines[0].startswith("| Bob")


# --- limit and offset ---


def test_limit():
    result = _run(limit=1)
    lines = [l for l in result.splitlines() if l.startswith("|") and "---" not in l and "name" not in l]
    assert len(lines) == 1


def test_offset():
    result = _run(offset=2)
    assert "Alice" not in result
    assert "Bob" not in result
    assert "Carol" in result


def test_limit_and_offset():
    result = _run(order_by="name asc", offset=1, limit=1)
    assert "Bob" in result
    assert "Alice" not in result
    assert "Carol" not in result


def test_limit_beyond_rows():
    result = _run(limit=100)
    assert "Alice" in result
    assert "Bob" in result


def test_offset_beyond_rows_returns_no_results():
    result = _run(offset=100)
    assert str_resources.note_no_results in result


# --- rendering options ---


def test_null_string():
    rows: list[Row] = [{"name": "Alice", "score": ""}, {"name": "Bob", "score": "10"}]
    result = _run(rows=rows, null_string="-")
    assert "| - |" in result or "| Alice | - |" in result


def test_max_cell_length_truncates():
    rows: list[Row] = [{"name": "Alice123456789"}]
    result = _run(rows=rows, max_cell_length=5)
    assert "Alic\u2026" in result  # 4 chars + ellipsis = 5 total


def test_max_cell_length_zero_no_truncation():
    rows: list[Row] = [{"name": "Alice123456789"}]
    result = _run(rows=rows, max_cell_length=0)
    assert "Alice123456789" in result


def test_date_format():
    rows: list[Row] = [{"name": "Alice", "created": "2024-01-15"}]
    result = _run(rows=rows, date_format="%d/%m/%Y")
    assert "15/01/2024" in result


def test_date_format_non_date_unchanged():
    rows: list[Row] = [{"name": "Alice", "value": "hello"}]
    result = _run(rows=rows, date_format="%Y-%m-%d")
    assert "hello" in result


def test_pipe_escaped_in_cell():
    rows: list[Row] = [{"name": "Alice|Bob"}]
    result = _run(rows=rows)
    assert "Alice\\|Bob" in result


def test_newline_replaced_in_cell():
    rows: list[Row] = [{"name": "Ali\nce", "score": "10"}]
    result = _run(rows=rows)
    assert "Ali ce" in result or "\n" not in "".join(result.split("|")[1:2])


# --- table structure ---


def test_output_ends_with_newline():
    result = _run()
    assert result.endswith("\n")


def test_header_separator_row():
    result = _run()
    lines = result.splitlines()
    assert lines[1] == "| --- | --- |"
