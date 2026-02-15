from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.span import Span
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.transformer_base import TransformerBase

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


@dataclass
class EmbedmFileParams:
    plan_node: PlanNode
    parent_document: Sequence[Fragment]
    file_cache: FileCache
    plugin_registry: PluginRegistry


class EmbedmFileTransformer(TransformerBase[EmbedmFileParams]):
    params_type = EmbedmFileParams

    def execute(self, params: EmbedmFileParams) -> str:
        """Compile a document by resolving spans and applying plugin transforms to directives."""
        if params.plan_node.document is None:
            return ""

        # step 1: load source content for span resolution
        # todo is this a programming error ?
        source_content, errors = params.file_cache.get_file(params.plan_node.directive.source)
        if errors or source_content is None:
            return ""

        # step 2: resolve spans into text, keep directives and strings as-is
        resolved: list[str | Directive] = _resolve_fragments(
            params.plan_node.document.fragments, source_content
        )

        # step 3: resolve directives via their plugins (DFS — children compiled on demand)
        child_lookup = {
            child.directive.source: child for child in (params.plan_node.children or [])
        }
        resolved = _resolve_directives(
            resolved, child_lookup, params.file_cache, params.plugin_registry
        )

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
        return None

    node = _find_or_create_node(directive, child_lookup)
    return plugin.transform(node, parent_document, file_cache, plugin_registry)


def _find_or_create_node(directive: Directive, child_lookup: dict[str, PlanNode]) -> PlanNode:
    """Look up the pre-planned child node, or create a leaf node for source-less directives."""
    if directive.source:
        child = child_lookup.get(directive.source)
        if child is not None:
            return child
    return PlanNode(directive=directive, status=[], document=None, children=None)
