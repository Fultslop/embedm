from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.span import Span
from embedm.domain.status_level import Status, StatusLevel
from embedm.plugins.plugin_context import PluginContext
from embedm.plugins.transformer_base import TransformerBase
from embedm_plugins.file.file_resources import render_error_note, str_resources


@dataclass
class FileParams:
    plan_node: PlanNode
    parent_document: Sequence[Fragment]
    context: PluginContext


class FileTransformer(TransformerBase[FileParams]):
    params_type = FileParams

    def execute(self, params: FileParams) -> str:
        """Compile a document by resolving spans and applying plugin transforms to directives."""
        assert params.plan_node.document is not None, "transformer requires a planned document"

        # step 1: load source content for span resolution (planner already validated and cached)
        source_content, errors = params.context.file_cache.get_file(params.plan_node.directive.source)
        assert not errors and source_content is not None, "source file should be cached after planning"

        # step 2: resolve spans into text, keep directives and strings as-is
        resolved: list[str | Directive] = _resolve_fragments(params.plan_node.document.fragments, source_content)

        # step 3: resolve directives via their plugins in plugin_sequence pass order (DFS per pass)
        # keyed by directive identity so multiple directives sharing a source are each matched to their own child
        child_lookup = {id(child.directive): child for child in (params.plan_node.children or [])}
        plugin_sequence = params.context.plugin_config.plugin_sequence if params.context.plugin_config else ()
        resolved = _compile_passes(resolved, child_lookup, params.context, plugin_sequence)

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


def _compile_passes(
    resolved: list[str | Directive],
    child_lookup: dict[int, PlanNode],
    context: PluginContext,
    plugin_sequence: tuple[str, ...],
) -> list[str | Directive]:
    """Run one pass per directive type in plugin_sequence order, replacing each type before the next runs."""
    if plugin_sequence:
        for directive_type in plugin_sequence:
            resolved = _resolve_directives(resolved, child_lookup, context, directive_type)
        return resolved
    return _resolve_directives(resolved, child_lookup, context)


def _resolve_directives(
    resolved: list[str | Directive],
    child_lookup: dict[int, PlanNode],
    context: PluginContext,
    directive_type: str | None = None,
) -> list[str | Directive]:
    """Resolve directives, optionally filtering to a single directive type."""
    result: list[str | Directive] = []

    for item in resolved:
        if not isinstance(item, Directive):
            result.append(item)
            continue

        if directive_type is not None and item.type != directive_type:
            result.append(item)
            continue

        transformed = _transform_directive(item, child_lookup, resolved, context)
        if transformed is not None:
            result.append(transformed)

    return result


def _transform_directive(
    directive: Directive,
    child_lookup: dict[int, PlanNode],
    parent_document: list[str | Directive],
    context: PluginContext,
) -> str | None:
    """Find the plugin for a directive and execute its transform."""
    assert context.plugin_registry is not None
    plugin = context.plugin_registry.find_plugin_by_directive_type(directive.type)
    if plugin is None:
        return render_error_note([f"no plugin registered for directive type '{directive.type}'"])

    node = _find_or_create_node(directive, child_lookup)

    if _node_has_errors(node) and node.document is None:
        error_msgs = [s.description for s in node.status if s.level in (StatusLevel.ERROR, StatusLevel.FATAL)]
        return render_error_note(error_msgs)

    result = plugin.transform(node, parent_document, context)
    if context.file_cache.max_embed_size > 0 and len(result) > context.file_cache.max_embed_size:
        return render_error_note(
            [str_resources.err_embed_size_exceeded.format(limit=context.file_cache.max_embed_size)]
        )
    return result


def _find_or_create_node(directive: Directive, child_lookup: dict[int, PlanNode]) -> PlanNode:
    """Look up the pre-planned child node, or create a leaf node for source-less directives."""
    child = child_lookup.get(id(directive))
    if child is not None:
        return child
    if directive.source:
        return PlanNode(
            directive=directive,
            status=[Status(StatusLevel.ERROR, f"source '{directive.source}' could not be processed")],
            document=None,
            children=None,
        )
    return PlanNode(directive=directive, status=[], document=None, children=None)


def _node_has_errors(node: PlanNode) -> bool:
    return any(s.level in (StatusLevel.ERROR, StatusLevel.FATAL) for s in node.status)
