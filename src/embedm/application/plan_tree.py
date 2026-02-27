from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel


def walk_nodes(node: PlanNode) -> Iterator[PlanNode]:
    """Yield every node in the plan tree in pre-order (depth-first)."""
    yield node
    for child in node.children or []:
        yield from walk_nodes(child)


def collect_tree_errors(root: PlanNode) -> list[Status]:
    """Return all ERROR/FATAL statuses from every node in the plan tree."""
    return [s for node in walk_nodes(root) for s in node.status if s.level in (StatusLevel.ERROR, StatusLevel.FATAL)]


def tree_has_level(root: PlanNode, levels: tuple[StatusLevel, ...]) -> bool:
    """Return True if any node in the plan tree has a status at one of the given levels."""
    return any(s.level in levels for node in walk_nodes(root) for s in node.status)


def count_nodes(root: PlanNode) -> int:
    """Count all nodes in the plan tree (root + all descendants)."""
    return 1 + sum(count_nodes(c) for c in (root.children or []))


def collect_embedded_sources(root: PlanNode, embed_type: str = "file") -> set[str]:
    """Return the resolved source paths of directives that merge content inline.

    Only sources from directives of `embed_type` are collected. Other directive types
    (recall, synopsis, query-path, table) read their source but do not merge it into
    the compiled output, so they must not be excluded from standalone compilation.
    """
    sources: set[str] = set()
    for node in walk_nodes(root):
        for child in node.children or []:
            if child.directive.source and child.directive.type == embed_type:
                sources.add(str(Path(child.directive.source).resolve()))
    return sources
