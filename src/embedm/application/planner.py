from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.parsing.directive_parser import parse_yaml_embed_blocks

from .embedm_context import EmbedmContext


def create_plan(directive: Directive, content: str, depth: int, context: EmbedmContext) -> PlanNode:
    """Build a validated plan tree from content, catching all issues before compilation."""
    # step 1: parse content into fragments
    fragments, parse_errors = parse_yaml_embed_blocks(content)
    if parse_errors:
        return _error_node(directive, parse_errors)

    # step 2: build the document
    document = Document(file_name=directive.source, fragments=fragments)
    directives = [f for f in fragments if isinstance(f, Directive)]

    # steps 3-4: validate directives and source files
    errors = _validate_directives(directives, depth, context)
    if errors:
        return _error_node(directive, errors)

    # step 6: recurse into source directives
    children = _build_children(directives, depth, context)

    return PlanNode(
        directive=directive,
        status=[Status(StatusLevel.OK, "plan created successfully")],
        document=document,
        children=children,
    )


def _validate_directives(
    directives: list[Directive], depth: int, context: EmbedmContext
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
            errors.extend(plugin.validate_directive(d))

    for d in directives:
        if not d.source:
            continue
        if depth >= context.config.max_recursion:
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
    directives: list[Directive], depth: int, context: EmbedmContext
) -> list[PlanNode]:
    """Recursively build child plan nodes for directives with sources."""
    children: list[PlanNode] = []

    for d in directives:
        if not d.source:
            continue
        source_content, load_errors = context.file_cache.get_file(d.source)
        if load_errors or source_content is None:
            continue
        child = create_plan(d, source_content, depth + 1, context)
        children.append(child)

    return children


def _error_node(directive: Directive, errors: list[Status]) -> PlanNode:
    """Create a PlanNode representing a failed plan step."""
    return PlanNode(directive=directive, status=errors, document=None, children=None)
