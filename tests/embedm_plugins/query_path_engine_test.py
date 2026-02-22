import pytest

from embedm_plugins.query_path_engine import parse_path, resolve


# --- parse_path ---


def test_parse_single_segment():
    assert parse_path("key") == ["key"]


def test_parse_nested_path():
    assert parse_path("a.b.c") == ["a", "b", "c"]


def test_parse_integer_segment():
    assert parse_path("servers.0.host") == ["servers", "0", "host"]


def test_parse_backtick_segment():
    assert parse_path("node.`value`.child") == ["node", "`value`", "child"]


def test_parse_backtick_at_start():
    assert parse_path("`value`.child") == ["`value`", "child"]


def test_parse_backtick_at_end():
    assert parse_path("node.`attributes`") == ["node", "`attributes`"]


def test_parse_dot_inside_backtick_is_not_split():
    assert parse_path("`a.b`") == ["`a.b`"]


# --- resolve ---


def test_resolve_simple_key():
    assert resolve({"key": "value"}, ["key"]) == "value"


def test_resolve_nested_keys():
    tree = {"a": {"b": {"c": 42}}}
    assert resolve(tree, ["a", "b", "c"]) == 42


def test_resolve_integer_index_on_list():
    tree = {"servers": [{"host": "localhost"}, {"host": "remote"}]}
    assert resolve(tree, ["servers", "0", "host"]) == "localhost"
    assert resolve(tree, ["servers", "1", "host"]) == "remote"


def test_resolve_missing_key_raises_key_error():
    with pytest.raises(KeyError):
        resolve({"a": 1}, ["b"])


def test_resolve_index_out_of_range_raises_index_error():
    with pytest.raises(IndexError):
        resolve([1, 2, 3], ["5"])


def test_resolve_non_integer_on_list_raises_key_error():
    with pytest.raises(KeyError):
        resolve([1, 2, 3], ["foo"])


def test_resolve_scalar_node_raises_key_error():
    with pytest.raises(KeyError):
        resolve("hello", ["key"])


def test_resolve_backtick_key_in_dict():
    tree = {"node": {"`value`": {"value": "content"}}}
    assert resolve(tree, ["node", "`value`"]) == {"value": "content"}


def test_resolve_empty_segments_returns_tree():
    tree = {"a": 1}
    assert resolve(tree, []) == tree


def test_resolve_null_value():
    assert resolve({"key": None}, ["key"]) is None


def test_resolve_bool_value():
    assert resolve({"flag": True}, ["flag"]) is True
