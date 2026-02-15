import os

from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.parsing.directive_parser import parse_yaml_embed_blocks
from embedm.plugins.plugin_configuration import PluginConfiguration

from .embedm_context import EmbedmContext

EMBEDM_FILE_DIRECTIVE_TYPE = "embedm_file"


def plan_file(file_name: str, context: EmbedmContext) -> PlanNode:
    """Create a plan for a file, using an embedm_file root directive."""
    root_directive = Directive(type=EMBEDM_FILE_DIRECTIVE_TYPE, source=file_name)
    content, errors = context.file_cache.get_file(file_name)
    if errors or content is None:
        return _error_node(
            root_directive,
            errors if errors else [Status(StatusLevel.ERROR, f"failed to load file '{file_name}'")],
        )
    return create_plan(root_directive, content, 0, context, frozenset({file_name}))


def create_plan(
    directive: Directive,
    content: str,
    depth: int,
    context: EmbedmContext,
    ancestors: frozenset[str] = frozenset(),
) -> PlanNode:
    """Build a validated plan tree from content, catching all issues before compilation."""
    # step 1: parse content into fragments
    fragments, parse_errors = parse_yaml_embed_blocks(content)
    if parse_errors:
        return _error_node(directive, parse_errors)

    # step 2: build the document
    document = Document(file_name=directive.source, fragments=fragments)
    directives = [f for f in fragments if isinstance(f, Directive)]

    # step 3: resolve relative source paths against the parent file's directory
    _resolve_source_paths(directives, directive.source)

    # steps 4-5: validate directives and source files
    plugin_config = PluginConfiguration(
        max_embed_size=context.config.max_embed_size,
        max_recursion=context.config.max_recursion,
    )
    errors = _validate_directives(directives, depth, ancestors, context, plugin_config)
    if errors:
        return _error_node(directive, errors)

    # step 6: recurse into source directives
    children = _build_children(directives, depth, ancestors, context)

    return PlanNode(
        directive=directive,
        status=[Status(StatusLevel.OK, "plan created successfully")],
        document=document,
        children=children,
    )


def _validate_directives(
    directives: list[Directive],
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
    plugin_config: PluginConfiguration,
) -> list[Status]:
    """Validate directives against the plugin registry and file cache."""
    errors: list[Status] = []

    for d in directives:
        plugin = context.plugin_registry.find_plugin_by_directive_type(d.type)
        if plugin is None:
            errors.append(
                Status(StatusLevel.ERROR, f"no plugin registered for directive type '{d.type}'")
            )
        else:
            errors.extend(plugin.validate_directive(d, plugin_config))

    for d in directives:
        if not d.source:
            continue
        if d.source in ancestors:
            errors.append(Status(StatusLevel.ERROR, f"circular dependency detected: '{d.source}'"))
        elif depth >= context.config.max_recursion:
            errors.append(
                Status(
                    StatusLevel.ERROR,
                    f"max recursion depth ({context.config.max_recursion}) reached",
                )
            )
        else:
            errors.extend(context.file_cache.validate(d.source))

    return errors


def _build_children(
    directives: list[Directive],
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
) -> list[PlanNode]:
    """Recursively build child plan nodes for directives with sources."""
    children: list[PlanNode] = []

    for d in directives:
        if not d.source:
            continue
        source_content, load_errors = context.file_cache.get_file(d.source)
        if load_errors or source_content is None:
            continue
        child = create_plan(d, source_content, depth + 1, context, ancestors | {d.source})
        children.append(child)

    return children


def _resolve_source_paths(directives: list[Directive], parent_source: str) -> None:
    """Resolve relative directive sources against the parent file's directory."""
    parent_dir = os.path.dirname(parent_source) if parent_source else ""
    if not parent_dir:
        return
    for d in directives:
        if d.source and not os.path.isabs(d.source):
            d.source = os.path.normpath(os.path.join(parent_dir, d.source))


def _error_node(directive: Directive, errors: list[Status]) -> PlanNode:
    """Create a PlanNode representing a failed plan step."""
    return PlanNode(directive=directive, status=errors, document=None, children=None)
