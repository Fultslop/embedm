from pathlib import Path

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
    resolved = str(Path(file_name).resolve())
    root_directive = Directive(type=EMBEDM_FILE_DIRECTIVE_TYPE, source=resolved)
    content, errors = context.file_cache.get_file(resolved)
    if errors or content is None:
        return _error_node(
            root_directive,
            errors if errors else [Status(StatusLevel.ERROR, f"failed to load file '{resolved}'")],
        )
    return create_plan(root_directive, content, 0, context, frozenset({resolved}))


def create_plan(
    directive: Directive,
    content: str,
    depth: int,
    context: EmbedmContext,
    ancestors: frozenset[str] = frozenset(),
) -> PlanNode:
    """Build a validated plan tree from content, collecting all errors without short-circuiting."""
    all_errors: list[Status] = []

    # step 1: parse content into fragments, resolving relative sources against parent directory
    base_dir = str(Path(directive.source).parent) if directive.source else ""
    fragments, parse_errors = parse_yaml_embed_blocks(content, base_dir=base_dir)
    all_errors.extend(parse_errors)

    # step 2: build the document (always, even with parse errors — fragments may be partial)
    document = Document(file_name=directive.source, fragments=fragments)
    directives = [f for f in fragments if isinstance(f, Directive)]

    # step 3: validate directives — collect errors and determine which sources are buildable
    plugin_config = PluginConfiguration(
        max_embed_size=context.config.max_embed_size,
        max_recursion=context.config.max_recursion,
    )
    validation_errors, buildable = _validate_directives(directives, depth, ancestors, context, plugin_config)
    all_errors.extend(validation_errors)

    # step 4: recurse into buildable source directives
    children = _build_children(buildable, depth, ancestors, context)

    if not all_errors:
        all_errors.append(Status(StatusLevel.OK, "plan created successfully"))

    return PlanNode(
        directive=directive,
        status=all_errors,
        document=document,
        children=children,
    )


def _validate_directives(
    directives: list[Directive],
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
    plugin_config: PluginConfiguration,
) -> tuple[list[Status], list[Directive]]:
    """Validate directives. Returns (all_errors, buildable_directives)."""
    errors: list[Status] = []
    buildable: list[Directive] = []

    for d in directives:
        plugin = context.plugin_registry.find_plugin_by_directive_type(d.type)
        if plugin is None:
            errors.append(Status(StatusLevel.ERROR, f"no plugin registered for directive type '{d.type}'"))
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
            source_errors = context.file_cache.validate(d.source)
            if source_errors:
                errors.extend(source_errors)
            else:
                buildable.append(d)

    return errors, buildable


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


def _error_node(directive: Directive, errors: list[Status]) -> PlanNode:
    """Create a PlanNode representing a failed plan step."""
    return PlanNode(directive=directive, status=errors, document=None, children=None)
