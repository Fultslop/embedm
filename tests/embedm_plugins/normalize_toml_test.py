import tomllib

import pytest

from embedm_plugins.normalize_toml import normalize


def test_simple_mapping():
    assert normalize('[project]\nversion = "1.0"') == {"project": {"version": "1.0"}}


def test_nested_mapping():
    result = normalize("[a]\n[a.b]\nc = 1")
    assert result == {"a": {"b": {"c": 1}}}


def test_array_of_tables():
    result = normalize("[[items]]\nid = 1\n[[items]]\nid = 2")
    assert result == {"items": [{"id": 1}, {"id": 2}]}


def test_inline_array():
    result = normalize("nums = [1, 2, 3]")
    assert result == {"nums": [1, 2, 3]}


def test_bool_values():
    result = normalize("t = true\nf = false")
    assert result == {"t": True, "f": False}


def test_integer_value():
    assert normalize("count = 42") == {"count": 42}


def test_invalid_toml_raises():
    with pytest.raises(tomllib.TOMLDecodeError):
        normalize("not = [valid toml")
