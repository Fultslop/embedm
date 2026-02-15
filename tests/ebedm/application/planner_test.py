from pathlib import Path
from unittest.mock import MagicMock

from embedm.application.embedm_context import EmbedmContext
from embedm.application.planner import create_plan, plan_file
from embedm.domain.directive import Directive
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_registry import PluginRegistry


def _make_context(
    tmp_path: Path,
    max_recursion: int = 10,
) -> EmbedmContext:
    config = MagicMock()
    config.max_recursion = max_recursion

    file_cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    registry = PluginRegistry()

    return EmbedmContext(config=config, file_cache=file_cache, plugin_registry=registry)


def _register_plugin(
    context: EmbedmContext,
    directive_type: str,
    validate_errors: list[Status] | None = None,
) -> MagicMock:
    plugin = MagicMock(spec=PluginBase)
    plugin.name = directive_type
    plugin.directive_type = directive_type
    plugin.validate_directive.return_value = validate_errors or []
    context.plugin_registry.lookup[directive_type] = plugin
    return plugin


# --- create_plan: happy path ---


def test_create_plan_no_directives(tmp_path: Path):
    context = _make_context(tmp_path)
    directive = Directive(type="root")
    content = "Just plain markdown\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.directive == directive
    assert plan.document is not None
    assert len(plan.document.fragments) == 1
    assert plan.children is not None
    assert len(plan.children) == 0
    assert any(s.level == StatusLevel.OK for s in plan.status)


def test_create_plan_directive_without_source(tmp_path: Path):
    context = _make_context(tmp_path)
    _register_plugin(context, "hello_world")
    directive = Directive(type="root")
    content = (
        "Before\n"
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
        "After\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.directive == directive
    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 0
    assert any(s.level == StatusLevel.OK for s in plan.status)


def test_create_plan_directive_with_source(tmp_path: Path):
    source_file = tmp_path / "include.md"
    source_file.write_text("Included content\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = (
        "Before\n"
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {source_file}\n"
        "```\n"
        "After\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.directive == directive
    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].directive.type == "file_embed"
    assert plan.children[0].directive.source == str(source_file)
    assert any(s.level == StatusLevel.OK for s in plan.status)


def test_create_plan_child_has_document(tmp_path: Path):
    source_file = tmp_path / "include.md"
    source_file.write_text("Child content\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {source_file}\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    child = plan.children[0]
    assert child.document is not None
    assert child.children is not None
    assert len(child.children) == 0
    assert any(s.level == StatusLevel.OK for s in child.status)


# --- create_plan: error cases ---


def test_create_plan_unknown_directive_type(tmp_path: Path):
    context = _make_context(tmp_path)
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: unknown_plugin\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.directive == directive
    assert plan.document is None
    assert plan.children is None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)


def test_create_plan_plugin_validation_fails(tmp_path: Path):
    context = _make_context(tmp_path)
    _register_plugin(
        context,
        "hello_world",
        validate_errors=[Status(StatusLevel.ERROR, "invalid directive")],
    )
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is None
    assert plan.children is None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)


def test_create_plan_source_file_not_found(tmp_path: Path):
    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {tmp_path / 'nonexistent.md'}\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is None
    assert plan.children is None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)


def test_create_plan_max_recursion_exceeded(tmp_path: Path):
    source_file = tmp_path / "include.md"
    source_file.write_text("content")

    context = _make_context(tmp_path, max_recursion=2)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {source_file}\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=2, context=context)

    assert plan.document is None
    assert plan.children is None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)


def test_create_plan_parser_errors_return_with_error(tmp_path: Path):
    context = _make_context(tmp_path)
    directive = Directive(type="root")
    content = (
        "Text before\n"
        "```yaml embedm\n"
        "type: hello_world\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is None
    assert plan.children is None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)


# --- create_plan: error collection ---


def test_create_plan_collects_multiple_errors(tmp_path: Path):
    context = _make_context(tmp_path)
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: unknown_one\n"
        "```\n"
        "```yaml embedm\n"
        "type: unknown_two\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is None
    assert plan.children is None
    error_count = sum(1 for s in plan.status if s.level == StatusLevel.ERROR)
    assert error_count >= 2


def test_create_plan_child_errors_dont_fail_parent(tmp_path: Path):
    source_file = tmp_path / "include.md"
    source_file.write_text(
        "```yaml embedm\n"
        "type: unknown_plugin\n"
        "```\n"
    )

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {source_file}\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    # Parent succeeds
    assert plan.document is not None
    assert any(s.level == StatusLevel.OK for s in plan.status)
    # Child has errors
    assert plan.children is not None
    assert len(plan.children) == 1
    assert any(s.level == StatusLevel.ERROR for s in plan.children[0].status)


# --- relative path resolution ---


def test_create_plan_resolves_relative_source_against_parent(tmp_path: Path):
    """A directive with a relative source is resolved against the parent file's directory."""
    subdir = tmp_path / "docs"
    subdir.mkdir()
    child_file = subdir / "child.md"
    child_file.write_text("child content\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    # Parent directive lives in subdir
    parent_directive = Directive(type="root", source=str(subdir / "root.md"))
    content = (
        "Before\n"
        "```yaml embedm\n"
        "type: file_embed\n"
        "source: ./child.md\n"
        "```\n"
    )

    plan = create_plan(parent_directive, content, depth=0, context=context)

    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    # Source should be resolved to the full path, not remain as ./child.md
    assert "child.md" in plan.children[0].directive.source
    assert plan.children[0].directive.source != "./child.md"


def test_plan_file_resolves_nested_relative_paths(tmp_path: Path):
    """End-to-end: plan_file resolves relative paths across nesting levels."""
    subdir = tmp_path / "docs"
    subdir.mkdir()
    root_file = subdir / "root.md"
    child_file = subdir / "chapter.md"

    child_file.write_text("chapter content\n")
    root_file.write_text(
        "# Root\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        "source: ./chapter.md\n"
        "```\n"
    )

    context = _make_context(tmp_path)
    _register_plugin(context, "embedm_file")

    plan = plan_file(str(root_file), context)

    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    assert str(child_file) in plan.children[0].directive.source


# --- circular dependency detection ---


def test_create_plan_detects_self_reference(tmp_path: Path):
    """A file that includes itself is detected as a cycle."""
    self_ref = tmp_path / "self.md"
    self_ref.write_text(
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {self_ref}\n"
        "```\n"
    )

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")

    plan = plan_file(str(self_ref), context)

    assert plan.document is None
    assert any("circular" in s.description.lower() for s in plan.status)


def test_create_plan_detects_indirect_cycle(tmp_path: Path):
    """A→B→A cycle is detected and reported as an error."""
    file_a = tmp_path / "a.md"
    file_b = tmp_path / "b.md"

    file_a.write_text(
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {file_b}\n"
        "```\n"
    )
    file_b.write_text(
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {file_a}\n"
        "```\n"
    )

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")

    plan = plan_file(str(file_a), context)

    # Root succeeds, but the child (b.md) should have a cycle error
    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    child = plan.children[0]
    assert child.document is None
    assert any("circular" in s.description.lower() for s in child.status)
