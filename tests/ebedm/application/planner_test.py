from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from unittest.mock import MagicMock

from embedm.application.embedm_context import EmbedmContext
from embedm.application.planner import create_plan, plan_content, plan_file
from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_registry import PluginRegistry
from embedm.plugins.normalization_base import NormalizationResult


def _make_context(
    tmp_path: Path,
    max_recursion: int = 10,
) -> EmbedmContext:
    config = MagicMock()
    config.max_recursion = max_recursion
    config.max_embed_size = 1024 * 1024
    config.verbosity = 2

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
    normalize_input_result: NormalizationResult | None = None,
) -> MagicMock:
    plugin = MagicMock(spec=PluginBase)
    plugin.name = directive_type
    plugin.directive_type = directive_type
    plugin.validate_directive.return_value = validate_errors or []
    plugin.normalize_input.return_value = normalize_input_result or NormalizationResult(normalized_data=None)
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
    content = "Before\n```yaml embedm\ntype: hello_world\n```\nAfter\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.directive == directive
    assert plan.document is not None
    assert plan.children is not None
    # source-less directives with a registered plugin get a child node (for normalize_input / artifact)
    assert len(plan.children) == 1
    assert plan.children[0].directive.type == "hello_world"
    assert plan.children[0].document is None
    assert any(s.level == StatusLevel.OK for s in plan.status)


def test_create_plan_directive_with_source(tmp_path: Path):
    source_file = tmp_path / "include.md"
    source_file.write_text("Included content\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = f"Before\n```yaml embedm\ntype: file_embed\nsource: {source_file}\n```\nAfter\n"

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
    content = f"```yaml embedm\ntype: file_embed\nsource: {source_file}\n```\n"

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
    content = "```yaml embedm\ntype: unknown_plugin\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.directive == directive
    assert plan.document is not None
    assert plan.children is not None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)


def test_create_plan_plugin_validation_fails(tmp_path: Path):
    context = _make_context(tmp_path)
    _register_plugin(
        context,
        "hello_world",
        validate_errors=[Status(StatusLevel.ERROR, "invalid directive")],
    )
    directive = Directive(type="root")
    content = "```yaml embedm\ntype: hello_world\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is not None
    assert plan.children is not None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)


def test_create_plan_source_file_not_found(tmp_path: Path):
    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = f"```yaml embedm\ntype: file_embed\nsource: {tmp_path / 'nonexistent.md'}\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].document is None
    assert any(s.level == StatusLevel.ERROR for s in plan.children[0].status)
    # Source errors live on the error child, not the parent
    assert any(s.level == StatusLevel.OK for s in plan.status)


def test_create_plan_max_recursion_exceeded(tmp_path: Path):
    source_file = tmp_path / "include.md"
    source_file.write_text("content")

    context = _make_context(tmp_path, max_recursion=2)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = f"```yaml embedm\ntype: file_embed\nsource: {source_file}\n```\n"

    plan = create_plan(directive, content, depth=2, context=context)

    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].document is None
    assert any("max recursion" in s.description for s in plan.children[0].status)
    # Source errors live on the error child, not the parent
    assert any(s.level == StatusLevel.OK for s in plan.status)


def test_create_plan_parser_errors_still_builds_partial_document(tmp_path: Path):
    """Unclosed fence: partial fragments are preserved alongside the error."""
    context = _make_context(tmp_path)
    directive = Directive(type="root")
    content = "Text before\n```yaml embedm\ntype: hello_world\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is not None
    assert plan.children is not None
    assert any(s.level == StatusLevel.ERROR for s in plan.status)
    # The text before the unclosed block is preserved as a fragment
    assert len(plan.document.fragments) >= 1


# --- create_plan: error collection ---


def test_create_plan_collects_multiple_errors(tmp_path: Path):
    context = _make_context(tmp_path)
    directive = Directive(type="root")
    content = "```yaml embedm\ntype: unknown_one\n```\n```yaml embedm\ntype: unknown_two\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is not None
    assert plan.children is not None
    error_count = sum(1 for s in plan.status if s.level == StatusLevel.ERROR)
    assert error_count >= 2


def test_create_plan_child_errors_dont_fail_parent(tmp_path: Path):
    source_file = tmp_path / "include.md"
    source_file.write_text("```yaml embedm\ntype: unknown_plugin\n```\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = f"```yaml embedm\ntype: file_embed\nsource: {source_file}\n```\n"

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
    content = "Before\n```yaml embedm\ntype: file_embed\nsource: ./child.md\n```\n"

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
    root_file.write_text("# Root\n```yaml embedm\ntype: file\nsource: ./chapter.md\n```\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file")

    plan = plan_file(str(root_file), context)

    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    assert str(child_file) in plan.children[0].directive.source


# --- circular dependency detection ---


def test_create_plan_detects_self_reference(tmp_path: Path):
    """A file that includes itself is detected as a cycle."""
    self_ref = tmp_path / "self.md"
    self_ref.write_text(f"```yaml embedm\ntype: file_embed\nsource: {self_ref}\n```\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")

    plan = plan_file(str(self_ref), context)

    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].document is None
    assert any("circular" in s.description.lower() for s in plan.children[0].status)
    # Source errors live on the error child, not the parent
    assert any(s.level == StatusLevel.OK for s in plan.status)


def test_create_plan_detects_indirect_cycle(tmp_path: Path):
    """A→B→A cycle is detected and reported as an error."""
    file_a = tmp_path / "a.md"
    file_b = tmp_path / "b.md"

    file_a.write_text(f"```yaml embedm\ntype: file_embed\nsource: {file_b}\n```\n")
    file_b.write_text(f"```yaml embedm\ntype: file_embed\nsource: {file_a}\n```\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")

    plan = plan_file(str(file_a), context)

    # Root and child (b.md) succeed; the cycle error is on b's error child for a.md
    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 1
    child_b = plan.children[0]
    assert child_b.document is not None
    assert any(s.level == StatusLevel.OK for s in child_b.status)
    # b.md's child is an error node for the cycle back to a.md
    assert child_b.children is not None
    assert len(child_b.children) == 1
    assert any("circular" in s.description.lower() for s in child_b.children[0].status)


# --- duplicate source handling ---


def test_create_plan_two_directives_same_source_produce_two_children(tmp_path: Path):
    """Two directives pointing at the same source file both get their own child node."""
    shared = tmp_path / "shared.md"
    shared.write_text("shared content\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = (
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {shared}\n"
        "```\n"
        "```yaml embedm\n"
        "type: file_embed\n"
        f"source: {shared}\n"
        "```\n"
    )

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.document is not None
    assert plan.children is not None
    assert len(plan.children) == 2
    assert plan.children[0].directive.source == str(shared)
    assert plan.children[1].directive.source == str(shared)


# --- normalize_input ---


def test_normalize_input_errors_produce_error_child(tmp_path: Path):
    """normalize_input errors create an error child node; the child document is None."""
    source_file = tmp_path / "data.csv"
    source_file.write_text("name,age\nAlice,30\n")

    context = _make_context(tmp_path)
    error = Status(StatusLevel.ERROR, "file contains no data rows.")
    _register_plugin(context, "table", normalize_input_result=NormalizationResult(normalized_data=None, errors=[error]))
    directive = Directive(type="root")
    content = f"```yaml embedm\ntype: table\nsource: {source_file}\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.children is not None
    assert len(plan.children) == 1
    child = plan.children[0]
    assert child.document is None
    assert any("data rows" in s.description for s in child.status)


def test_normalize_input_artifact_stored_on_child(tmp_path: Path):
    """normalize_input artifact is attached to the child PlanNode."""
    source_file = tmp_path / "data.csv"
    source_file.write_text("name,age\nAlice,30\n")

    artifact = [{"name": "Alice", "age": "30"}]
    context = _make_context(tmp_path)
    _register_plugin(context, "table", normalize_input_result=NormalizationResult(normalized_data=artifact))
    directive = Directive(type="root")
    content = f"```yaml embedm\ntype: table\nsource: {source_file}\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].normalized_data == artifact


def test_normalize_input_no_op_does_not_block_child(tmp_path: Path):
    """Default no-op normalize_input (no errors, no artifact) still builds the child."""
    source_file = tmp_path / "include.md"
    source_file.write_text("content\n")

    context = _make_context(tmp_path)
    _register_plugin(context, "file_embed")
    directive = Directive(type="root")
    content = f"```yaml embedm\ntype: file_embed\nsource: {source_file}\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].document is not None
    assert plan.children[0].normalized_data is None


# --- normalize_input on root ---


def test_plan_file_normalize_input_is_called(tmp_path: Path):
    """normalize_input is called on the root directive when using plan_file."""
    root_file = tmp_path / "root.md"
    root_file.write_text("# Root content\n")

    context = _make_context(tmp_path)
    context.config.root_directive_type = "root_type"
    plugin = _register_plugin(context, "root_type")

    plan_file(str(root_file), context)

    plugin.normalize_input.assert_called_once()
    assert plugin.normalize_input.call_args[0][0].type == "root_type"


def test_plan_file_normalize_input_errors_produce_error_root(tmp_path: Path):
    """normalize_input errors on the root directive produce an error node (document is None)."""
    root_file = tmp_path / "root.md"
    root_file.write_text("# Root content\n")

    error = Status(StatusLevel.ERROR, "root input is invalid")
    context = _make_context(tmp_path)
    context.config.root_directive_type = "root_type"
    _register_plugin(context, "root_type", normalize_input_result=NormalizationResult(normalized_data=None, errors=[error]))

    plan = plan_file(str(root_file), context)

    assert plan.document is None
    assert any("root input is invalid" in s.description for s in plan.status)


def test_plan_file_normalize_input_artifact_stored_on_root(tmp_path: Path):
    """normalize_input artifact is attached to the root PlanNode when using plan_file."""
    root_file = tmp_path / "root.md"
    root_file.write_text("# Root content\n")

    artifact = {"parsed": True}
    context = _make_context(tmp_path)
    context.config.root_directive_type = "root_type"
    _register_plugin(context, "root_type", normalize_input_result=NormalizationResult(normalized_data=artifact))

    plan = plan_file(str(root_file), context)

    assert plan.normalized_data == artifact


def test_plan_content_normalize_input_is_called(tmp_path: Path):
    """normalize_input is called on the root directive when using plan_content."""
    context = _make_context(tmp_path)
    context.config.root_directive_type = "root_type"
    plugin = _register_plugin(context, "root_type")

    plan_content("# Content\n", context)

    plugin.normalize_input.assert_called_once()
    assert plugin.normalize_input.call_args[0][0].type == "root_type"


def test_plan_content_normalize_input_errors_produce_error_root(tmp_path: Path):
    """normalize_input errors on the root directive produce an error node (document is None)."""
    error = Status(StatusLevel.ERROR, "stdin input is invalid")
    context = _make_context(tmp_path)
    context.config.root_directive_type = "root_type"
    _register_plugin(context, "root_type", normalize_input_result=NormalizationResult(normalized_data=None, errors=[error]))

    plan = plan_content("# Content\n", context)

    assert plan.document is None
    assert any("stdin input is invalid" in s.description for s in plan.status)


def test_plan_content_normalize_input_artifact_stored_on_root(tmp_path: Path):
    """normalize_input artifact is attached to the root PlanNode when using plan_content."""
    artifact = {"parsed": True}
    context = _make_context(tmp_path)
    context.config.root_directive_type = "root_type"
    _register_plugin(context, "root_type", normalize_input_result=NormalizationResult(normalized_data=artifact))

    plan = plan_content("# Content\n", context)

    assert plan.normalized_data == artifact


# --- deprecated directive type and option remapping ---


class _DeprecatedTypePlugin(PluginBase):
    name = "new_plugin"
    directive_type = "new_type"
    deprecated_directive_types = ["old-type"]

    def transform(self, plan_node: PlanNode, parent_document: Sequence[Fragment], context=None) -> str:
        return ""


class _DeprecatedOptionPlugin(PluginBase):
    name = "opt_plugin"
    directive_type = "opt_type"
    deprecated_option_names = {"new_opt": ["old_opt"]}

    def transform(self, plan_node: PlanNode, parent_document: Sequence[Fragment], context=None) -> str:
        return ""


def test_create_plan_remaps_deprecated_directive_type(tmp_path: Path):
    """A deprecated directive type is remapped to canonical before validation. WARNING collected."""
    context = _make_context(tmp_path)
    context.plugin_registry.lookup[_DeprecatedTypePlugin.name] = _DeprecatedTypePlugin()
    directive = Directive(type="root")
    content = "```yaml embedm\ntype: old-type\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].directive.type == "new_type"
    warning_statuses = [s for s in plan.status if s.level == StatusLevel.WARNING]
    assert len(warning_statuses) == 1
    assert "old-type" in warning_statuses[0].description
    assert "new_type" in warning_statuses[0].description


def test_create_plan_remaps_deprecated_option_name(tmp_path: Path):
    """Deprecated option names are remapped to canonical before validation. WARNING collected."""
    context = _make_context(tmp_path)
    context.plugin_registry.lookup[_DeprecatedOptionPlugin.name] = _DeprecatedOptionPlugin()
    directive = Directive(type="root")
    content = "```yaml embedm\ntype: opt_type\nold_opt: some_value\n```\n"

    plan = create_plan(directive, content, depth=0, context=context)

    assert plan.children is not None
    assert len(plan.children) == 1
    assert plan.children[0].directive.options.get("new_opt") == "some_value"
    assert "old_opt" not in plan.children[0].directive.options
    warning_statuses = [s for s in plan.status if s.level == StatusLevel.WARNING]
    assert len(warning_statuses) == 1
    assert "old_opt" in warning_statuses[0].description
    assert "new_opt" in warning_statuses[0].description
