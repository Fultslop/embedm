from pathlib import Path
from unittest.mock import MagicMock

from embedm.application.embedm_context import EmbedmContext
from embedm.application.planner import plan_file
from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.plan_node import PlanNode
from embedm.domain.span import Span
from embedm.domain.status_level import StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_registry import PluginRegistry
from embedm_plugins.embedm_file_plugin import EmbedmFilePlugin


def _make_context(tmp_path: Path, max_recursion: int = 10) -> EmbedmContext:
    config = MagicMock()
    config.max_recursion = max_recursion
    file_cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    registry = PluginRegistry()
    registry.lookup["embedm file plugin"] = EmbedmFilePlugin()
    return EmbedmContext(config=config, file_cache=file_cache, plugin_registry=registry)


def _register_mock_plugin(
    context: EmbedmContext,
    directive_type: str,
    transform_result: str = "",
) -> MagicMock:
    plugin = MagicMock(spec=PluginBase)
    plugin.name = directive_type
    plugin.directive_type = directive_type
    plugin.validate_directive.return_value = []
    plugin.transform.return_value = transform_result
    context.plugin_registry.lookup[directive_type] = plugin
    return plugin


# --- happy path: plain text ---


def test_plain_text_no_directives(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("Just plain text\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert result == "Just plain text\n"


def test_multiline_plain_text(tmp_path: Path):
    content = "Line one\nLine two\nLine three\n"
    source = tmp_path / "input.md"
    source.write_text(content)

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert result == content


# --- happy path: simple directive ---


def test_directive_without_source(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text(
        "Before\n"
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
        "After\n"
    )

    context = _make_context(tmp_path)
    _register_mock_plugin(context, "hello_world", transform_result="hello embedded world!")
    plan = plan_file(str(source), context)
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert "Before\n" in result
    assert "hello embedded world!" in result
    assert "After\n" in result


def test_multiple_directives(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text(
        "Start\n"
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
        "Middle\n"
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
        "End\n"
    )

    context = _make_context(tmp_path)
    _register_mock_plugin(context, "hello_world", transform_result="HW")
    plan = plan_file(str(source), context)
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert "Start\n" in result
    assert "Middle\n" in result
    assert "End\n" in result
    assert result.count("HW") == 2


# --- happy path: source directive (DFS recursion) ---


def test_directive_with_source_compiles_child(tmp_path: Path):
    child_file = tmp_path / "child.md"
    child_file.write_text("Child content\n")

    source = tmp_path / "input.md"
    source.write_text(
        "Before\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        f"source: {child_file}\n"
        "```\n"
        "After\n"
    )

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert "Before\n" in result
    assert "Child content\n" in result
    assert "After\n" in result


def test_nested_recursion(tmp_path: Path):
    grandchild = tmp_path / "grandchild.md"
    grandchild.write_text("Grandchild\n")

    child = tmp_path / "child.md"
    child.write_text(
        "Child start\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        f"source: {grandchild}\n"
        "```\n"
        "Child end\n"
    )

    source = tmp_path / "input.md"
    source.write_text(
        "Root start\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        f"source: {child}\n"
        "```\n"
        "Root end\n"
    )

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert "Root start\n" in result
    assert "Child start\n" in result
    assert "Grandchild\n" in result
    assert "Child end\n" in result
    assert "Root end\n" in result


def test_source_with_mixed_directives(tmp_path: Path):
    child = tmp_path / "child.md"
    child.write_text(
        "Child has\n"
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
        "inside\n"
    )

    source = tmp_path / "input.md"
    source.write_text(
        "Root\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        f"source: {child}\n"
        "```\n"
    )

    context = _make_context(tmp_path)
    _register_mock_plugin(context, "hello_world", transform_result="HW")
    plan = plan_file(str(source), context)
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert "Root\n" in result
    assert "Child has\n" in result
    assert "HW" in result
    assert "inside\n" in result


# --- edge cases ---


def test_no_document_returns_empty(tmp_path: Path):
    node = PlanNode(
        directive=Directive(type="embedm_file", source="missing.md"),
        status=[],
        document=None,
        children=None,
    )
    plugin = EmbedmFilePlugin()
    file_cache = FileCache(1024, 4096, [str(tmp_path)])
    registry = PluginRegistry()

    result = plugin.transform(node, [], file_cache, registry)

    assert result == ""


def test_no_file_cache_returns_empty():
    node = PlanNode(
        directive=Directive(type="embedm_file", source="input.md"),
        status=[],
        document=Document(file_name="input.md", fragments=[Span(0, 5)]),
        children=None,
    )
    plugin = EmbedmFilePlugin()

    result = plugin.transform(node, [])

    assert result == ""


def test_directive_with_unknown_plugin_is_skipped(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text(
        "Before\n"
        "```yaml embedm\n"
        "type: unknown_plugin\n"
        "```\n"
        "After\n"
    )

    context = _make_context(tmp_path)
    # register unknown_plugin so planner doesn't reject it, but don't register in file plugin's context
    _register_mock_plugin(context, "unknown_plugin")
    plan = plan_file(str(source), context)

    # now remove the plugin so the file plugin can't find it
    del context.plugin_registry.lookup["unknown_plugin"]
    plugin = EmbedmFilePlugin()

    result = plugin.transform(plan, [], context.file_cache, context.plugin_registry)

    assert "Before\n" in result
    assert "After\n" in result


# --- validate_directive ---


def test_validate_directive_missing_source():
    plugin = EmbedmFilePlugin()
    config = MagicMock()
    directive = Directive(type="embedm_file")

    errors = plugin.validate_directive(directive, config)

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_with_source():
    plugin = EmbedmFilePlugin()
    config = MagicMock()
    directive = Directive(type="embedm_file", source="some/file.md")

    errors = plugin.validate_directive(directive, config)

    assert len(errors) == 0
