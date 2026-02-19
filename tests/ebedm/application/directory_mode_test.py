"""Tests for directory mode: file expansion, deduplication, and output."""

from __future__ import annotations

from pathlib import Path

from embedm.application.orchestration import (
    _collect_embedded_sources,
    _expand_directory_input,
    _glob_base,
)
from embedm.domain.directive import Directive
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel

# --- _expand_directory_input ---


def test_expand_plain_directory(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("a")
    (tmp_path / "b.md").write_text("b")
    (tmp_path / "c.txt").write_text("c")

    result = _expand_directory_input(str(tmp_path))

    assert len(result) == 2
    assert any("a.md" in p for p in result)
    assert any("b.md" in p for p in result)
    assert not any("c.txt" in p for p in result)


def test_expand_star_pattern(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("a")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.md").write_text("nested")

    result = _expand_directory_input(str(tmp_path / "*"))

    # non-recursive: only top-level .md files
    assert len(result) == 1
    assert any("a.md" in p for p in result)


def test_expand_double_star_pattern(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("a")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.md").write_text("nested")

    result = _expand_directory_input(str(tmp_path / "**"))

    # recursive: both top-level and nested .md files
    assert len(result) == 2
    assert any("a.md" in p for p in result)
    assert any("nested.md" in p for p in result)


def test_expand_mid_path_double_star_pattern(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("a")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.md").write_text("nested")

    # Pattern with wildcard in the middle: base/**/*.md
    result = _expand_directory_input(str(tmp_path / "**" / "*.md"))

    assert len(result) == 2
    assert any("a.md" in p for p in result)
    assert any("nested.md" in p for p in result)


def test_expand_empty_directory(tmp_path: Path) -> None:
    result = _expand_directory_input(str(tmp_path))

    assert result == []


# --- _glob_base ---


def test_glob_base_double_star_at_end(tmp_path: Path) -> None:
    assert _glob_base(str(tmp_path / "**")) == tmp_path


def test_glob_base_double_star_in_middle(tmp_path: Path) -> None:
    assert _glob_base(str(tmp_path / "**" / "*.md")) == tmp_path


def test_glob_base_single_star(tmp_path: Path) -> None:
    assert _glob_base(str(tmp_path / "*")) == tmp_path


def test_glob_base_bare_star_returns_current_dir() -> None:
    assert _glob_base("*") == Path(".")


# --- _collect_embedded_sources ---


def test_collect_embedded_sources_from_children() -> None:
    child = PlanNode(
        directive=Directive(type="file", source="/tmp/child.md"),
        status=[Status(StatusLevel.OK, "ok")],
        document=None,
        children=None,
    )
    root = PlanNode(
        directive=Directive(type="file", source="/tmp/root.md"),
        status=[Status(StatusLevel.OK, "ok")],
        document=None,
        children=[child],
    )

    sources: set[str] = set()
    _collect_embedded_sources(root, sources)

    assert len(sources) == 1
    assert str(Path("/tmp/child.md").resolve()) in sources


def test_collect_embedded_sources_nested() -> None:
    grandchild = PlanNode(
        directive=Directive(type="file", source="/tmp/grandchild.md"),
        status=[Status(StatusLevel.OK, "ok")],
        document=None,
        children=None,
    )
    child = PlanNode(
        directive=Directive(type="file", source="/tmp/child.md"),
        status=[Status(StatusLevel.OK, "ok")],
        document=None,
        children=[grandchild],
    )
    root = PlanNode(
        directive=Directive(type="file", source="/tmp/root.md"),
        status=[Status(StatusLevel.OK, "ok")],
        document=None,
        children=[child],
    )

    sources: set[str] = set()
    _collect_embedded_sources(root, sources)

    assert len(sources) == 2
    assert str(Path("/tmp/child.md").resolve()) in sources
    assert str(Path("/tmp/grandchild.md").resolve()) in sources


def test_collect_embedded_sources_no_children() -> None:
    root = PlanNode(
        directive=Directive(type="file", source="/tmp/root.md"),
        status=[Status(StatusLevel.OK, "ok")],
        document=None,
        children=None,
    )

    sources: set[str] = set()
    _collect_embedded_sources(root, sources)

    assert len(sources) == 0
