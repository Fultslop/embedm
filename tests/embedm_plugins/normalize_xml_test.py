import xml.etree.ElementTree as ET

import pytest

from embedm_plugins.query_path_normalize_xml import normalize


def test_element_with_attributes():
    result = normalize('<node attr_a="foo" attr_b="123"/>')
    assert result == {"node": {"attributes": {"attr_a": "foo", "attr_b": "123"}}}


def test_element_with_text():
    result = normalize("<node>hello</node>")
    assert result == {"node": {"value": "hello"}}


def test_element_with_attributes_and_text():
    result = normalize('<node attr="x">hello</node>')
    assert result == {"node": {"attributes": {"attr": "x"}, "value": "hello"}}


def test_element_with_child():
    result = normalize("<root><child/></root>")
    assert result == {"root": {"child": {}}}


def test_element_with_child_and_attributes():
    result = normalize('<root><child x="1"/></root>')
    assert result == {"root": {"child": {"attributes": {"x": "1"}}}}


def test_element_with_text_and_child():
    result = normalize("<root>hello<child/></root>")
    assert result == {"root": {"value": "hello", "child": {}}}


def test_multiple_children_same_tag():
    result = normalize("<root><item>a</item><item>b</item></root>")
    assert result == {"root": {"item": [{"value": "a"}, {"value": "b"}]}}


def test_reserved_key_child_value():
    result = normalize("<root><value>content</value></root>")
    assert "`value`" in result["root"]
    assert result["root"]["`value`"] == {"value": "content"}


def test_reserved_key_child_attributes():
    result = normalize("<root><attributes x='1'/></root>")
    assert "`attributes`" in result["root"]
    assert result["root"]["`attributes`"] == {"attributes": {"x": "1"}}


def test_empty_element():
    result = normalize("<root/>")
    assert result == {"root": {}}


def test_invalid_xml_raises():
    with pytest.raises(ET.ParseError):
        normalize("<unclosed>")
