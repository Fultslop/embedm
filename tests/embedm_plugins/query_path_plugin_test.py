from unittest.mock import MagicMock

from embedm.domain.directive import Directive
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import StatusLevel
from embedm_plugins.query_path_resources import str_resources
from embedm_plugins.query_path_plugin import QueryPathPlugin, _QueryPathArtifact


def _make_plan_node(source: str, options: dict[str, str] | None = None, artifact: object = None) -> PlanNode:
    directive = Directive(type="query-path", source=source, options=options or {})
    node = PlanNode(directive=directive, status=[], document=MagicMock())
    node.artifact = artifact
    return node


# --- validate_directive ---


def test_validate_missing_source():
    plugin = QueryPathPlugin()
    errors = plugin.validate_directive(Directive(type="query-path"))
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "source" in errors[0].description


def test_validate_unsupported_extension():
    plugin = QueryPathPlugin()
    errors = plugin.validate_directive(Directive(type="query-path", source="data.csv"))
    assert any("csv" in e.description for e in errors)


def test_validate_supported_toml():
    plugin = QueryPathPlugin()
    assert plugin.validate_directive(Directive(type="query-path", source="data.toml")) == []


def test_validate_supported_json():
    plugin = QueryPathPlugin()
    assert plugin.validate_directive(Directive(type="query-path", source="data.json")) == []


def test_validate_supported_yaml():
    plugin = QueryPathPlugin()
    assert plugin.validate_directive(Directive(type="query-path", source="data.yaml")) == []


def test_validate_supported_yml():
    plugin = QueryPathPlugin()
    assert plugin.validate_directive(Directive(type="query-path", source="data.yml")) == []


def test_validate_supported_xml():
    plugin = QueryPathPlugin()
    assert plugin.validate_directive(Directive(type="query-path", source="data.xml")) == []


def test_validate_format_without_path_is_error():
    plugin = QueryPathPlugin()
    errors = plugin.validate_directive(Directive(type="query-path", source="data.json", options={"format": "v: {value}"}))
    assert len(errors) == 1
    assert "path" in errors[0].description


def test_validate_format_missing_placeholder_is_error():
    plugin = QueryPathPlugin()
    errors = plugin.validate_directive(
        Directive(type="query-path", source="data.json", options={"path": "version", "format": "no placeholder"})
    )
    assert len(errors) == 1
    assert "{value}" in errors[0].description


def test_validate_format_with_path_and_placeholder_is_valid():
    plugin = QueryPathPlugin()
    errors = plugin.validate_directive(
        Directive(type="query-path", source="data.json", options={"path": "version", "format": "v: {value}"})
    )
    assert errors == []


# --- validate_input: JSON ---


def test_validate_input_json_scalar():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "version"})
    result = plugin.validate_input(directive, '{"version": "1.2.3"}')
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.value == "1.2.3"
    assert not result.artifact.is_full_document


def test_validate_input_json_nested_path():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "a.b.c"})
    result = plugin.validate_input(directive, '{"a": {"b": {"c": 42}}}')
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.value == 42


def test_validate_input_json_integer_index():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "items.1"})
    result = plugin.validate_input(directive, '{"items": ["a", "b", "c"]}')
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.value == "b"


def test_validate_input_json_no_path_is_full_document():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json")
    raw = '{"version": "1.0"}'
    result = plugin.validate_input(directive, raw)
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.is_full_document
    assert result.artifact.raw_content == raw
    assert result.artifact.lang_tag == "json"


def test_validate_input_json_invalid_path():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "missing.key"})
    result = plugin.validate_input(directive, '{"version": "1.0"}')
    assert len(result.errors) == 1
    assert result.errors[0].level == StatusLevel.ERROR
    assert result.artifact is None


def test_validate_input_invalid_json():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "version"})
    result = plugin.validate_input(directive, "not json")
    assert len(result.errors) == 1
    assert result.errors[0].level == StatusLevel.ERROR
    assert result.artifact is None


# --- validate_input: YAML ---


def test_validate_input_yaml_scalar():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.yaml", options={"path": "project.version"})
    result = plugin.validate_input(directive, "project:\n  version: 0.6.0")
    assert result.errors == []
    assert result.artifact is not None
    assert str(result.artifact.value) == "0.6.0"


def test_validate_input_yml_lang_tag():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.yml")
    result = plugin.validate_input(directive, "key: value")
    assert result.artifact is not None
    assert result.artifact.lang_tag == "yaml"


def test_validate_input_invalid_yaml():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.yaml", options={"path": "key"})
    result = plugin.validate_input(directive, "key: [unclosed")
    assert len(result.errors) == 1
    assert result.artifact is None


# --- validate_input: XML ---


def test_validate_input_xml_attribute():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.xml", options={"path": "server.attributes.host"})
    result = plugin.validate_input(directive, '<server host="localhost"/>')
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.value == "localhost"


def test_validate_input_xml_text_content():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.xml", options={"path": "root.value"})
    result = plugin.validate_input(directive, "<root>hello</root>")
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.value == "hello"


def test_validate_input_xml_backtick_escape():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.xml", options={"path": "root.`value`.child"})
    xml = "<root><value><child>found</child></value></root>"
    result = plugin.validate_input(directive, xml)
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.value == {"value": "found"}


def test_validate_input_invalid_xml():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.xml", options={"path": "root"})
    result = plugin.validate_input(directive, "<unclosed>")
    assert len(result.errors) == 1
    assert result.artifact is None


# --- validate_input: TOML ---


def test_validate_input_toml_scalar():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pyproject.toml", options={"path": "project.version"})
    result = plugin.validate_input(directive, '[project]\nversion = "0.6.0"')
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.value == "0.6.0"


def test_validate_input_toml_no_path_is_full_document():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.toml")
    raw = '[project]\nversion = "1.0"'
    result = plugin.validate_input(directive, raw)
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.is_full_document
    assert result.artifact.lang_tag == "toml"


def test_validate_input_invalid_toml():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="cfg.toml", options={"path": "key"})
    result = plugin.validate_input(directive, "not = [valid toml")
    assert len(result.errors) == 1
    assert result.artifact is None


def test_validate_input_format_scalar_stores_format_str():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "version", "format": "v: {value}"})
    result = plugin.validate_input(directive, '{"version": "1.2.3"}')
    assert result.errors == []
    assert result.artifact is not None
    assert result.artifact.format_str == "v: {value}"


def test_validate_input_format_non_scalar_dict_is_error():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "meta", "format": "x: {value}"})
    result = plugin.validate_input(directive, '{"meta": {"key": "val"}}')
    assert len(result.errors) == 1
    assert result.artifact is None


def test_validate_input_format_non_scalar_list_is_error():
    plugin = QueryPathPlugin()
    directive = Directive(type="query-path", source="pkg.json", options={"path": "items", "format": "x: {value}"})
    result = plugin.validate_input(directive, '{"items": [1, 2, 3]}')
    assert len(result.errors) == 1
    assert result.artifact is None


# --- transform ---


def test_transform_no_document():
    plugin = QueryPathPlugin()
    node = PlanNode(Directive(type="query-path", source="pkg.json"), status=[], document=None)
    assert plugin.transform(node, []) == ""


def test_transform_no_artifact():
    plugin = QueryPathPlugin()
    node = _make_plan_node("pkg.json", artifact=None)
    assert plugin.transform(node, []) == ""


def test_transform_scalar_artifact():
    plugin = QueryPathPlugin()
    artifact = _QueryPathArtifact(value="1.2.3", raw_content="", lang_tag="json", is_full_document=False)
    node = _make_plan_node("pkg.json", artifact=artifact)
    assert plugin.transform(node, []) == "1.2.3\n"


def test_transform_full_document_artifact():
    plugin = QueryPathPlugin()
    raw = '{"version": "1.0"}'
    artifact = _QueryPathArtifact(value=None, raw_content=raw, lang_tag="json", is_full_document=True)
    node = _make_plan_node("pkg.json", artifact=artifact)
    result = plugin.transform(node, [])
    assert result.startswith("```json")
    assert raw in result


def test_transform_with_format_str():
    plugin = QueryPathPlugin()
    artifact = _QueryPathArtifact(value="0.6.0", raw_content="", lang_tag="json", is_full_document=False, format_str="version: {value}")
    node = _make_plan_node("pkg.json", artifact=artifact)
    assert plugin.transform(node, []) == "version: 0.6.0\n"
