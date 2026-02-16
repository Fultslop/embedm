"""Integration tests: full pipeline from file to compiled output, no mocks."""

from pathlib import Path

from embedm.application.configuration import Configuration
from embedm.application.embedm_context import EmbedmContext
from embedm.application.planner import plan_file
from embedm.domain.status_level import StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_registry import PluginRegistry


def _build_context(tmp_path: Path) -> EmbedmContext:
    """Build a real pipeline context with loaded plugins, rooted at tmp_path."""
    config = Configuration()
    file_cache = FileCache(
        max_file_size=config.max_file_size,
        memory_limit=config.max_memory,
        allowed_paths=[str(tmp_path)],
    )
    registry = PluginRegistry()
    registry.load_plugins()
    return EmbedmContext(config=config, file_cache=file_cache, plugin_registry=registry)


def _compile(file_path: Path, context: EmbedmContext) -> str:
    """Plan and compile a file, returning the compiled output."""
    plan = plan_file(str(file_path), context)
    assert plan.document is not None, f"planning failed: {[s.description for s in plan.status]}"

    plugin = context.plugin_registry.find_plugin_by_directive_type(plan.directive.type)
    assert plugin is not None
    return plugin.transform(plan, [], context.file_cache, context.plugin_registry)


# --- test 1: single file with hello_world directive ---


def test_hello_world_directive_compiles(tmp_path: Path):
    """A file with text and a hello_world block produces the expected output."""
    source = tmp_path / "input.md"
    source.write_text(
        "Before\n"
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
        "After\n"
    )

    context = _build_context(tmp_path)
    result = _compile(source, context)

    assert "Before\n" in result
    assert "hello embedded world!" in result
    assert "After\n" in result


# --- test 2: nested file embedding with relative paths ---


def test_nested_file_embed_with_relative_path(tmp_path: Path):
    """A root file embedding a child via relative path inlines the child content."""
    child = tmp_path / "chapter.md"
    child.write_text("Chapter content\n")

    root = tmp_path / "root.md"
    root.write_text(
        "Root intro\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        "source: ./chapter.md\n"
        "```\n"
        "Root outro\n"
    )

    context = _build_context(tmp_path)
    result = _compile(root, context)

    assert "Root intro\n" in result
    assert "Chapter content\n" in result
    assert "Root outro\n" in result


# --- test 3: three-level nesting across directories ---


def test_three_level_nesting_across_directories(tmp_path: Path):
    """root.md → sub/middle.md → sub/deep/leaf.md all resolve and inline correctly."""
    sub = tmp_path / "sub"
    deep = sub / "deep"
    deep.mkdir(parents=True)

    leaf = deep / "leaf.md"
    leaf.write_text("Leaf content\n")

    middle = sub / "middle.md"
    middle.write_text(
        "Middle start\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        "source: ./deep/leaf.md\n"
        "```\n"
        "Middle end\n"
    )

    root = tmp_path / "root.md"
    root.write_text(
        "Root start\n"
        "```yaml embedm\n"
        "type: embedm_file\n"
        "source: ./sub/middle.md\n"
        "```\n"
        "Root end\n"
    )

    context = _build_context(tmp_path)
    result = _compile(root, context)

    assert "Root start\n" in result
    assert "Middle start\n" in result
    assert "Leaf content\n" in result
    assert "Middle end\n" in result
    assert "Root end\n" in result


# --- test 4: circular dependency produces clean error ---


def test_circular_dependency_produces_error(tmp_path: Path):
    """A→B→A cycle is caught during planning without crash or infinite loop."""
    file_a = tmp_path / "a.md"
    file_b = tmp_path / "b.md"

    file_a.write_text(
        "```yaml embedm\n"
        "type: embedm_file\n"
        f"source: {file_b}\n"
        "```\n"
    )
    file_b.write_text(
        "```yaml embedm\n"
        "type: embedm_file\n"
        f"source: {file_a}\n"
        "```\n"
    )

    context = _build_context(tmp_path)
    plan = plan_file(str(file_a), context)

    # Root plans successfully
    assert plan.document is not None
    assert any(s.level == StatusLevel.OK for s in plan.status)

    # Child (b.md) detects the cycle
    assert plan.children is not None
    assert len(plan.children) == 1
    child = plan.children[0]
    assert child.document is not None
    assert any("circular" in s.description.lower() for s in child.status)

    # Compilation renders the cycle as a visible caution block
    result = _compile(file_a, context)
    assert "> [!CAUTION]" in result
