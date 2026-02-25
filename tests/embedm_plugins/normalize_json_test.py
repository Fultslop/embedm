import json

import pytest

from embedm_plugins.query_path.query_path_normalize_json import normalize


def test_scalar_string():
    assert normalize('"hello"') == "hello"


def test_scalar_number():
    assert normalize("42") == 42


def test_simple_object():
    assert normalize('{"key": "value"}') == {"key": "value"}


def test_nested_object():
    result = normalize('{"a": {"b": {"c": 1}}}')
    assert result == {"a": {"b": {"c": 1}}}


def test_array():
    assert normalize("[1, 2, 3]") == [1, 2, 3]


def test_object_with_array():
    result = normalize('{"arr": [1, 2, 3]}')
    assert result == {"arr": [1, 2, 3]}


def test_null_value():
    assert normalize('{"key": null}') == {"key": None}


def test_bool_values():
    result = normalize('{"t": true, "f": false}')
    assert result == {"t": True, "f": False}


def test_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        normalize("not json")


def test_empty_object():
    assert normalize("{}") == {}
