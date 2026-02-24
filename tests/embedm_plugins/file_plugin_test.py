from pathlib import Path
from unittest.mock import MagicMock

import pytest

from embedm.application.embedm_context import EmbedmContext
from embedm.application.planner import plan_file
from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.plan_node import PlanNode
from embedm.domain.span import Span
from embedm.domain.status_level import StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_context import PluginContext
from embedm.plugins.plugin_registry import PluginRegistry
from embedm_plugins.file_plugin import FilePlugin


def _make_context(tmp_path: Path, max_recursion: int = 10) -> EmbedmContext:
    config = MagicMock()
    config.max_recursion = max_recursion
    config.verbosity = 2
    file_cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    registry = PluginRegistry()
    registry.lookup["embedm file plugin"] = FilePlugin()
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
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert result == "Just plain text\n"


def test_multiline_plain_text(tmp_path: Path):
    content = "Line one\nLine two\nLine three\n"
    source = tmp_path / "input.md"
    source.write_text(content)

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert result == content


# --- happy path: simple directive ---


def test_directive_without_source(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("Before\n```yaml embedm\ntype: hello_world\n```\nAfter\n")

    context = _make_context(tmp_path)
    _register_mock_plugin(context, "hello_world", transform_result="hello embedded world!")
    plan = plan_file(str(source), context)
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Before\n" in result
    assert "hello embedded world!" in result
    assert "After\n" in result


def test_multiple_directives(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text(
        "Start\n```yaml embedm\ntype: hello_world\n```\nMiddle\n```yaml embedm\ntype: hello_world\n```\nEnd\n"
    )

    context = _make_context(tmp_path)
    _register_mock_plugin(context, "hello_world", transform_result="HW")
    plan = plan_file(str(source), context)
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Start\n" in result
    assert "Middle\n" in result
    assert "End\n" in result
    assert result.count("HW") == 2


# --- happy path: source directive (DFS recursion) ---


def test_directive_with_source_compiles_child(tmp_path: Path):
    child_file = tmp_path / "child.md"
    child_file.write_text("Child content\n")

    source = tmp_path / "input.md"
    source.write_text(f"Before\n```yaml embedm\ntype: file\nsource: {child_file}\n```\nAfter\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Before\n" in result
    assert "Child content\n" in result
    assert "After\n" in result


def test_nested_recursion(tmp_path: Path):
    grandchild = tmp_path / "grandchild.md"
    grandchild.write_text("Grandchild\n")

    child = tmp_path / "child.md"
    child.write_text(f"Child start\n```yaml embedm\ntype: file\nsource: {grandchild}\n```\nChild end\n")

    source = tmp_path / "input.md"
    source.write_text(f"Root start\n```yaml embedm\ntype: file\nsource: {child}\n```\nRoot end\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Root start\n" in result
    assert "Child start\n" in result
    assert "Grandchild\n" in result
    assert "Child end\n" in result
    assert "Root end\n" in result


def test_source_with_mixed_directives(tmp_path: Path):
    child = tmp_path / "child.md"
    child.write_text("Child has\n```yaml embedm\ntype: hello_world\n```\ninside\n")

    source = tmp_path / "input.md"
    source.write_text(f"Root\n```yaml embedm\ntype: file\nsource: {child}\n```\n")

    context = _make_context(tmp_path)
    _register_mock_plugin(context, "hello_world", transform_result="HW")
    plan = plan_file(str(source), context)
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Root\n" in result
    assert "Child has\n" in result
    assert "HW" in result
    assert "inside\n" in result


# --- edge cases ---


def test_no_document_returns_empty(tmp_path: Path):
    node = PlanNode(
        directive=Directive(type="file", source="missing.md"),
        status=[],
        document=None,
        children=None,
    )
    plugin = FilePlugin()
    file_cache = FileCache(1024, 4096, [str(tmp_path)])
    registry = PluginRegistry()

    result = plugin.transform(node, [], PluginContext(file_cache, registry))

    assert result == ""


def test_no_file_cache_asserts():
    """Missing file_cache is a coding error — orchestration must provide it."""
    node = PlanNode(
        directive=Directive(type="file", source="input.md"),
        status=[],
        document=Document(file_name="input.md", fragments=[Span(0, 5)]),
        children=None,
    )
    plugin = FilePlugin()

    with pytest.raises(AssertionError):
        plugin.transform(node, [])


def test_unknown_plugin_renders_error_note(tmp_path: Path):
    """Unknown plugin at compile time renders a visible caution block."""
    source = tmp_path / "input.md"
    source.write_text("Before\n```yaml embedm\ntype: unknown_plugin\n```\nAfter\n")

    context = _make_context(tmp_path)
    _register_mock_plugin(context, "unknown_plugin")
    plan = plan_file(str(source), context)

    # remove the plugin to simulate it being unavailable at compile time
    del context.plugin_registry.lookup["unknown_plugin"]
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Before\n" in result
    assert "After\n" in result
    assert "> [!CAUTION]" in result
    assert "unknown_plugin" in result


def test_source_not_in_children_renders_error_note(tmp_path: Path):
    """A directive whose source wasn't built by the planner renders an error note."""
    source = tmp_path / "input.md"
    source.write_text(f"Before\n```yaml embedm\ntype: file\nsource: {tmp_path / 'missing.md'}\n```\nAfter\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin = FilePlugin()

    result = plugin.transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Before\n" in result
    assert "After\n" in result
    assert "> [!CAUTION]" in result
    assert "missing.md" in result


# --- multi-pass compilation ---


def test_toc_above_file_embed_sees_embedded_headings(tmp_path: Path):
    """With multi-pass compilation, a toc directive placed before a file embed sees the embedded headings."""
    from embedm_plugins.toc_plugin import ToCPlugin

    child = tmp_path / "chapter.md"
    child.write_text("## Chapter from file\n\nContent here.\n")

    source = tmp_path / "root.md"
    source.write_text(
        "# Root\n"
        "```yaml embedm\ntype: toc\n```\n"
        f"```yaml embedm\ntype: file\nsource: {child}\n```\n"
    )

    context = _make_context(tmp_path)
    context.plugin_registry.lookup[ToCPlugin().name] = ToCPlugin()
    plan = plan_file(str(source), context)
    plugin_config = PluginConfiguration(max_embed_size=0, max_recursion=10, plugin_sequence=("file", "toc"))
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry, plugin_config))

    assert "Chapter from file" in result
    assert result.index("- Chapter from file") < result.index("## Chapter from file")


def test_single_pass_fallback_without_plugin_sequence(tmp_path: Path):
    """Without a plugin_sequence, compilation falls back to single-pass (backward compat)."""
    child = tmp_path / "child.md"
    child.write_text("Child content\n")

    source = tmp_path / "input.md"
    source.write_text(f"Before\n```yaml embedm\ntype: file\nsource: {child}\n```\nAfter\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)

    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Before\n" in result
    assert "Child content\n" in result
    assert "After\n" in result


# --- validate_directive ---


def test_validate_directive_missing_source():
    plugin = FilePlugin()
    config = MagicMock()
    directive = Directive(type="file")

    errors = plugin.validate_directive(directive, config)

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_with_source():
    plugin = FilePlugin()
    config = MagicMock()
    directive = Directive(type="file", source="some/file.md")

    errors = plugin.validate_directive(directive, config)

    assert len(errors) == 0


# --- max_embed_size enforcement ---


def _make_context_with_embed_limit(tmp_path: Path, max_embed_size: int) -> EmbedmContext:
    config = MagicMock()
    config.max_recursion = 10
    config.verbosity = 2
    file_cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
        max_embed_size=max_embed_size,
    )
    registry = PluginRegistry()
    registry.lookup["embedm file plugin"] = FilePlugin()
    return EmbedmContext(config=config, file_cache=file_cache, plugin_registry=registry)


def test_embed_size_exceeded_renders_error_note(tmp_path: Path):
    """A directive whose output exceeds max_embed_size renders a caution block."""
    source = tmp_path / "input.md"
    source.write_text("Before\n```yaml embedm\ntype: hello_world\n```\nAfter\n")

    context = _make_context_with_embed_limit(tmp_path, max_embed_size=5)
    _register_mock_plugin(context, "hello_world", transform_result="hello world!")  # 12 bytes > 5

    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Before\n" in result
    assert "After\n" in result
    assert "> [!CAUTION]" in result
    assert "max_embed_size" in result
    assert "hello world!" not in result


def test_embed_size_within_limit_passes_through(tmp_path: Path):
    """A directive whose output is within max_embed_size is returned unchanged."""
    source = tmp_path / "input.md"
    source.write_text("Before\n```yaml embedm\ntype: hello_world\n```\nAfter\n")

    context = _make_context_with_embed_limit(tmp_path, max_embed_size=100)
    _register_mock_plugin(context, "hello_world", transform_result="hello world!")

    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "hello world!" in result
    assert "> [!CAUTION]" not in result


def test_embed_size_zero_disables_limit(tmp_path: Path):
    """max_embed_size=0 disables output size enforcement."""
    source = tmp_path / "input.md"
    source.write_text("Before\n```yaml embedm\ntype: hello_world\n```\nAfter\n")

    context = _make_context_with_embed_limit(tmp_path, max_embed_size=0)
    large_output = "x" * 10000
    _register_mock_plugin(context, "hello_world", transform_result=large_output)

    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert large_output in result
    assert "> [!CAUTION]" not in result


# --- non-markdown source: code block wrapping ---


def test_non_markdown_source_wrapped_in_code_block(tmp_path: Path):
    code_file = tmp_path / "hello.cs"
    code_file.write_text("public class Hello { }\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "```cs" in result
    assert "public class Hello" in result


# --- validate_directive: extraction options ---


def test_validate_directive_exclusive_region_and_lines():
    plugin = FilePlugin()
    directive = Directive(type="file", source="foo.cs", options={"region": "r", "lines": "1..5"})

    errors = plugin.validate_directive(directive)

    assert any("exclusive" in e.description or "one of" in e.description for e in errors)
    assert all(e.level == StatusLevel.ERROR for e in errors)


def test_validate_directive_exclusive_region_and_symbol():
    plugin = FilePlugin()
    directive = Directive(type="file", source="foo.cs", options={"region": "r", "symbol": "MyClass"})

    errors = plugin.validate_directive(directive)

    assert len(errors) >= 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_invalid_lines_format():
    plugin = FilePlugin()
    directive = Directive(type="file", source="foo.cs", options={"lines": "1-5"})

    errors = plugin.validate_directive(directive)

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_valid_lines_format():
    plugin = FilePlugin()
    for valid in ("10", "5..10", "10..", "..10"):
        directive = Directive(type="file", source="foo.cs", options={"lines": valid})
        assert plugin.validate_directive(directive) == []


def test_validate_directive_symbol_unsupported_extension():
    plugin = FilePlugin()
    directive = Directive(type="file", source="foo.py", options={"symbol": "MyClass"})

    errors = plugin.validate_directive(directive)

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_symbol_supported_extension():
    plugin = FilePlugin()
    directive = Directive(type="file", source="foo.cs", options={"symbol": "MyClass"})

    assert plugin.validate_directive(directive) == []


# --- region extraction ---


def test_region_extraction_from_code_file(tmp_path: Path):
    code_file = tmp_path / "service.cs"
    code_file.write_text(
        "public class S {\n"
        "    // md.start: doWork\n"
        "    public void DoWork() { }\n"
        "    // md.end: doWork\n"
        "}\n"
    )

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nregion: doWork\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "DoWork" in result
    assert "class S" not in result
    assert "> [!CAUTION]" not in result


def test_region_not_found_renders_error(tmp_path: Path):
    code_file = tmp_path / "service.cs"
    code_file.write_text("public class S { }\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nregion: missing\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "> [!CAUTION]" in result
    assert "missing" in result


# --- line range extraction ---


def test_line_extraction_from_code_file(tmp_path: Path):
    code_file = tmp_path / "data.cs"
    code_file.write_text("line1\nline2\nline3\nline4\nline5\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nlines: 2..4\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "line2" in result
    assert "line4" in result
    assert "line1" not in result
    assert "line5" not in result


# --- symbol extraction ---


def test_symbol_extraction_from_cs_file(tmp_path: Path):
    code_file = tmp_path / "calculator.cs"
    code_file.write_text(
        "public class Calculator\n"
        "{\n"
        "    public int Add(int a, int b)\n"
        "    {\n"
        "        return a + b;\n"
        "    }\n"
        "}\n"
    )

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nsymbol: Add\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "Add" in result
    assert "return a + b" in result
    assert "class Calculator" not in result
    assert "> [!CAUTION]" not in result


def test_title_option_prepends_bold_label(tmp_path: Path):
    code_file = tmp_path / "util.cs"
    code_file.write_text("public class Util { }\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\ntitle: My Utility\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert '**"My Utility"**' in result
    assert result.index('**"My Utility"**') < result.index("```cs")


def test_link_option_falls_back_to_filename_without_compiled_dir(tmp_path: Path):
    code_file = tmp_path / "util.cs"
    code_file.write_text("public class Util { }\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nlink: true\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "[link util.cs](util.cs)" in result
    assert result.index("[link util.cs]") < result.index("```cs")


def test_link_option_uses_compiled_dir_for_path(tmp_path: Path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    code_file = src_dir / "util.cs"
    code_file.write_text("public class Util { }\n")

    source = src_dir / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nlink: true\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    plugin_config = PluginConfiguration(max_embed_size=0, max_recursion=10, compiled_dir=str(out_dir))
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry, plugin_config))

    assert "[link util.cs](../src/util.cs)" in result


def test_line_numbers_range_with_lines_option(tmp_path: Path):
    code_file = tmp_path / "data.cs"
    code_file.write_text("line1\nline2\nline3\nline4\nline5\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nlines: 2..4\nline_numbers_range: true\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "(lines 2..4)" in result
    assert result.index("(lines 2..4)") < result.index("```cs")


def test_line_numbers_range_without_lines_option_shows_nothing(tmp_path: Path):
    code_file = tmp_path / "data.cs"
    code_file.write_text("public class X { }\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nline_numbers_range: true\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    # line_numbers_range with no lines option produces no range header
    assert result.startswith("```cs")


def test_all_header_options_ordered_title_range_link(tmp_path: Path):
    code_file = tmp_path / "util.cs"
    code_file.write_text("line1\nline2\nline3\n")

    source = tmp_path / "input.md"
    source.write_text(
        f"```yaml embedm\ntype: file\nsource: {code_file}\n"
        f"title: My Label\nlines: 1..2\nline_numbers_range: true\nlink: true\n```\n"
    )

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    title_pos = result.index('**"My Label"**')
    range_pos = result.index("(lines 1..2)")
    link_pos = result.index("[link util.cs]")
    assert title_pos < range_pos < link_pos


def test_symbol_not_found_renders_error(tmp_path: Path):
    code_file = tmp_path / "calculator.cs"
    code_file.write_text("public class Calc { }\n")

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nsymbol: Missing\n```\n")

    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry))

    assert "> [!CAUTION]" in result
    assert "Missing" in result


# --- plugin config schema and semantic validation ---


def test_get_plugin_config_schema_returns_region_keys():
    schema = FilePlugin().get_plugin_config_schema()
    assert schema is not None
    assert "region_start" in schema
    assert "region_end" in schema
    assert schema["region_start"] is str
    assert schema["region_end"] is str


def test_validate_plugin_config_valid_templates_no_errors():
    errors = FilePlugin().validate_plugin_config(
        {"region_start": "region:{tag}", "region_end": "endregion:{tag}"}
    )
    assert errors == []


def test_validate_plugin_config_missing_tag_in_region_start_is_error():
    errors = FilePlugin().validate_plugin_config({"region_start": "region_start"})
    assert len(errors) == 1
    assert "region_start" in errors[0].description
    assert "{tag}" in errors[0].description


def test_validate_plugin_config_missing_tag_in_region_end_is_error():
    errors = FilePlugin().validate_plugin_config({"region_end": "region_end"})
    assert len(errors) == 1
    assert "region_end" in errors[0].description


def test_validate_plugin_config_absent_keys_no_error():
    # Missing keys use hardcoded defaults — not an error.
    errors = FilePlugin().validate_plugin_config({})
    assert errors == []


def test_region_extraction_with_custom_marker(tmp_path: Path):
    code_file = tmp_path / "hello.py"
    code_file.write_text(
        "# region:greet\ndef greet(): pass\n# endregion:greet\n"
    )

    source = tmp_path / "input.md"
    source.write_text(f"```yaml embedm\ntype: file\nsource: {code_file}\nregion: greet\n```\n")

    plugin_config = PluginConfiguration(
        max_embed_size=0,
        max_recursion=10,
        plugin_settings={
            "embedm_plugins.file_plugin": {
                "region_start": "region:{tag}",
                "region_end": "endregion:{tag}",
            }
        },
    )
    context = _make_context(tmp_path)
    plan = plan_file(str(source), context)
    result = FilePlugin().transform(plan, [], PluginContext(context.file_cache, context.plugin_registry, plugin_config))

    assert "def greet(): pass" in result
    assert "> [!CAUTION]" not in result
