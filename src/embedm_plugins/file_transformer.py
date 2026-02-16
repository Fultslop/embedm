from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.span import Span
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.transformer_base import TransformerBase

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


@dataclass
class FileParams:
    plan_node: PlanNode
    parent_document: Sequence[Fragment]
    file_cache: FileCache
    plugin_registry: PluginRegistry


class FileTransformer(TransformerBase[FileParams]):
    params_type = FileParams

    def execute(self, params: FileParams) -> str:
        """Compile a document by resolving spans and applying plugin transforms to directives."""
        assert params.plan_node.document is not None, "transformer requires a planned document"

        # step 1: load source content for span resolution (planner already validated and cached)
        source_content, errors = params.file_cache.get_file(params.plan_node.directive.source)
        assert not errors and source_content is not None, "source file should be cached after planning"

        # step 2: resolve spans into text, keep directives and strings as-is
        resolved: list[str | Directive] = _resolve_fragments(params.plan_node.document.fragments, source_content)

        # step 3: resolve directives via their plugins (DFS — children compiled on demand)
        # TODO: dict keyed by source loses duplicates when two directives share a source file
        child_lookup = {child.directive.source: child for child in (params.plan_node.children or [])}
        resolved = _resolve_directives(resolved, child_lookup, params.file_cache, params.plugin_registry)

        return "".join(s for s in resolved if isinstance(s, str))


def _resolve_fragments(fragments: list[Fragment], source_content: str) -> list[str | Directive]:
    """Resolve spans to text slices, pass through directives and strings as-is."""
    resolved: list[str | Directive] = []
    for fragment in fragments:
        if isinstance(fragment, Span):
            resolved.append(source_content[fragment.offset : fragment.offset + fragment.length])
        elif isinstance(fragment, (Directive, str)):
            resolved.append(fragment)
    return resolved


def _resolve_directives(
    resolved: list[str | Directive],
    child_lookup: dict[str, PlanNode],
    file_cache: FileCache,
    plugin_registry: PluginRegistry,
) -> list[str | Directive]:
    """Resolve each directive by finding its plugin and calling transform."""
    result: list[str | Directive] = []
    for item in resolved:
        if not isinstance(item, Directive):
            result.append(item)
            continue

        transformed = _transform_directive(item, child_lookup, result, file_cache, plugin_registry)
        if transformed is not None:
            result.append(transformed)

    return result


def _transform_directive(
    directive: Directive,
    child_lookup: dict[str, PlanNode],
    parent_document: list[str | Directive],
    file_cache: FileCache,
    plugin_registry: PluginRegistry,
) -> str | None:
    """Find the plugin for a directive and execute its transform."""
    plugin = plugin_registry.find_plugin_by_directive_type(directive.type)
    if plugin is None:
        return _render_error_note([f"no plugin registered for directive type '{directive.type}'"])

    node = _find_or_create_node(directive, child_lookup)

    if _node_has_errors(node) and node.document is None:
        error_msgs = [s.description for s in node.status if s.level in (StatusLevel.ERROR, StatusLevel.FATAL)]
        return _render_error_note(error_msgs)

    return plugin.transform(node, parent_document, file_cache, plugin_registry)


def _find_or_create_node(directive: Directive, child_lookup: dict[str, PlanNode]) -> PlanNode:
    """Look up the pre-planned child node, or create a leaf node for source-less directives."""
    if directive.source:
        child = child_lookup.get(directive.source)
        if child is not None:
            return child
        return PlanNode(
            directive=directive,
            status=[Status(StatusLevel.ERROR, f"source '{directive.source}' could not be processed")],
            document=None,
            children=None,
        )
    return PlanNode(directive=directive, status=[], document=None, children=None)


def _render_error_note(messages: list[str]) -> str:
    """Render error messages as a GitHub-flavored markdown caution block."""
    lines = ["> [!CAUTION]"]
    for msg in messages:
        lines.append(f"> **embedm:** {msg}")
    return "\n".join(lines) + "\n"


def _node_has_errors(node: PlanNode) -> bool:
    return any(s.level in (StatusLevel.ERROR, StatusLevel.FATAL) for s in node.status)
