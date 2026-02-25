from embedm.domain.status_level import StatusLevel
from embedm_plugins.table.table_validation import (
    CsvTsvTableValidation,
    CsvTsvValidationParams,
    JsonTableValidation,
    JsonValidationParams,
)

Row = dict[str, str]

_CSV_CONTENT = "name,age\nAlice,30\nBob,25\n"
_TSV_CONTENT = "name\tage\nAlice\t30\nBob\t25\n"
_JSON_CONTENT = '[{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]'


# --- CsvTsvTableValidation ---


def test_csv_valid_returns_rows():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_CSV_CONTENT, delimiter=",", select="", order_by="")
    )
    assert result.errors == []
    assert result.normalized_data == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]


def test_tsv_valid_returns_rows():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_TSV_CONTENT, delimiter="\t", select="", order_by="")
    )
    assert result.errors == []
    assert result.normalized_data == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]


def test_csv_empty_returns_error():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content="name,age\n", delimiter=",", select="", order_by="")
    )
    assert len(result.errors) == 1
    assert result.errors[0].level == StatusLevel.ERROR
    assert result.normalized_data is None


def test_csv_select_valid_column_ok():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_CSV_CONTENT, delimiter=",", select="name", order_by="")
    )
    assert result.errors == []
    assert result.normalized_data is not None


def test_csv_select_unknown_column_returns_error():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_CSV_CONTENT, delimiter=",", select="missing", order_by="")
    )
    assert any("missing" in e.description for e in result.errors)
    assert result.normalized_data is None


def test_csv_select_invalid_expression_returns_error():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_CSV_CONTENT, delimiter=",", select="col a b c", order_by="")
    )
    assert any(e.level == StatusLevel.ERROR for e in result.errors)
    assert result.normalized_data is None


def test_csv_order_by_valid_ok():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_CSV_CONTENT, delimiter=",", select="", order_by="name asc")
    )
    assert result.errors == []


def test_csv_order_by_invalid_expression_returns_error():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_CSV_CONTENT, delimiter=",", select="", order_by="col a b")
    )
    assert any(e.level == StatusLevel.ERROR for e in result.errors)
    assert result.normalized_data is None


def test_csv_select_with_alias_valid():
    result = CsvTsvTableValidation().validate(
        CsvTsvValidationParams(content=_CSV_CONTENT, delimiter=",", select="name as person", order_by="")
    )
    assert result.errors == []
    assert result.normalized_data is not None


# --- JsonTableValidation ---


def test_json_valid_returns_rows():
    result = JsonTableValidation().validate(
        JsonValidationParams(content=_JSON_CONTENT, select="", order_by="")
    )
    assert result.errors == []
    assert result.normalized_data == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]


def test_json_invalid_syntax_returns_error():
    result = JsonTableValidation().validate(
        JsonValidationParams(content="not json", select="", order_by="")
    )
    assert any(e.level == StatusLevel.ERROR for e in result.errors)
    assert result.normalized_data is None


def test_json_not_array_returns_error():
    result = JsonTableValidation().validate(
        JsonValidationParams(content='{"key": "val"}', select="", order_by="")
    )
    assert any("array" in e.description for e in result.errors)
    assert result.normalized_data is None


def test_json_array_not_objects_returns_error():
    result = JsonTableValidation().validate(
        JsonValidationParams(content="[1, 2, 3]", select="", order_by="")
    )
    assert any("objects" in e.description for e in result.errors)
    assert result.normalized_data is None


def test_json_empty_array_returns_error():
    result = JsonTableValidation().validate(
        JsonValidationParams(content="[]", select="", order_by="")
    )
    assert len(result.errors) == 1
    assert result.errors[0].level == StatusLevel.ERROR
    assert result.normalized_data is None


def test_json_select_unknown_column_returns_error():
    result = JsonTableValidation().validate(
        JsonValidationParams(content=_JSON_CONTENT, select="missing", order_by="")
    )
    assert any("missing" in e.description for e in result.errors)
    assert result.normalized_data is None


def test_json_bool_values_parsed_correctly():
    content = '[{"active": true, "name": "Alice"}]'
    result = JsonTableValidation().validate(
        JsonValidationParams(content=content, select="", order_by="")
    )
    assert result.errors == []
    assert result.normalized_data == [{"active": "true", "name": "Alice"}]


def test_json_null_values_parsed_as_empty_string():
    content = '[{"name": "Alice", "score": null}]'
    result = JsonTableValidation().validate(
        JsonValidationParams(content=content, select="", order_by="")
    )
    assert result.errors == []
    assert result.normalized_data == [{"name": "Alice", "score": ""}]
