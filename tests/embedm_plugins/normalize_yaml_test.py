import pytest
import yaml

from embedm_plugins.query_path.query_path_normalize_yaml import normalize


def test_simple_mapping():
    assert normalize("key: value") == {"key": "value"}


def test_nested_mapping():
    result = normalize("a:\n  b:\n    c: 1")
    assert result == {"a": {"b": {"c": 1}}}


def test_sequence():
    assert normalize("- 1\n- 2\n- 3") == [1, 2, 3]


def test_mapping_with_sequence():
    result = normalize("arr:\n  - 1\n  - 2")
    assert result == {"arr": [1, 2]}


def test_null_value():
    assert normalize("key: null") == {"key": None}


def test_bool_values():
    result = normalize("t: true\nf: false")
    assert result == {"t": True, "f": False}


def test_null_document():
    assert normalize("") is None


def test_invalid_yaml_raises():
    with pytest.raises(yaml.YAMLError):
        normalize("key: [unclosed")
