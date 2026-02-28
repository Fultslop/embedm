from pathlib import Path

from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_util import to_relative
from embedm.parsing.directive_parser import parse_yaml_embed_blocks
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_registry import PluginRegistry

from .application_resources import str_resources
from .embedm_context import EmbedmContext


def plan_content(content: str, context: EmbedmContext) -> PlanNode:
    """Create a plan for raw content, using cwd as the base directory."""
    source = str(Path.cwd() / "<stdin>")
    root_directive = Directive(type=context.config.root_directive_type, source=source)
    plugin_config = PluginConfiguration(
        max_embed_size=context.config.max_embed_size,
        max_recursion=context.config.max_recursion,
    )
    return _validate_and_plan(root_directive, content, 0, frozenset(), context, plugin_config)


def plan_file(file_name: str, context: EmbedmContext) -> PlanNode:
    """Create a plan for a file, using the configured root directive type."""
    resolved = str(Path(file_name).resolve())
    root_directive = Directive(type=context.config.root_directive_type, source=resolved)
    content, errors = context.file_cache.get_file(resolved)
    if errors or content is None:
        return _error_node(
            root_directive,
            errors if errors else [Status(StatusLevel.ERROR, f"failed to load file '{to_relative(resolved)}'")],
        )
    plugin_config = PluginConfiguration(
        max_embed_size=context.config.max_embed_size,
        max_recursion=context.config.max_recursion,
    )
    return _validate_and_plan(root_directive, content, 0, frozenset({resolved}), context, plugin_config)


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

    # step 2b: remap deprecated directive types and option names in-place
    all_errors.extend(_remap_deprecated(directives, context.plugin_registry))

    # step 3: validate directives — collect errors and determine which sources are buildable
    plugin_config = PluginConfiguration(
        max_embed_size=context.config.max_embed_size,
        max_recursion=context.config.max_recursion,
    )
    all_errors.extend(_check_plugins(directives, context, plugin_config))
    buildable, error_children = _check_sources(directives, depth, ancestors, context)

    # step 4: recurse into buildable source directives, validate source-less directives, include error children
    sourceless_nodes = _validate_sourceless_directives(directives, context, plugin_config)
    children = _build_children(buildable, depth, ancestors, context, plugin_config) + error_children + sourceless_nodes

    if not all_errors:
        all_errors.append(Status(StatusLevel.OK, "plan created successfully"))

    return PlanNode(
        directive=directive,
        status=all_errors,
        document=document,
        children=children,
    )


def _remap_deprecated(directives: list[Directive], registry: PluginRegistry) -> list[Status]:
    """Remap deprecated directive types and option names in-place.

    Returns WARNING statuses for all deprecated names encountered.
    """
    warnings: list[Status] = []
    for d in directives:
        canonical, is_deprecated = registry.resolve_directive_type(d.type)
        if is_deprecated:
            warnings.append(
                Status(
                    StatusLevel.WARNING,
                    str_resources.warn_deprecated_directive_type.format(old_type=d.type, new_type=canonical),
                )
            )
            d.type = canonical
        plugin = registry.find_plugin_by_directive_type(d.type)
        if plugin is not None:
            warnings.extend(plugin.remap_deprecated_options(d))
    return warnings


def _check_plugins(
    directives: list[Directive],
    context: EmbedmContext,
    plugin_config: PluginConfiguration,
) -> list[Status]:
    """Check plugin existence and run validate_directive for each directive. Returns all errors."""
    errors: list[Status] = []
    for d in directives:
        plugin = context.plugin_registry.find_plugin_by_directive_type(d.type)
        if plugin is None:
            msg = str_resources.err_plan_no_plugin.format(directive_type=d.type)
            errors.append(Status(StatusLevel.ERROR, msg))
        else:
            errors.extend(plugin.validate_directive(d, plugin_config))
    return errors


def _check_sources(
    directives: list[Directive],
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
) -> tuple[list[Directive], list[PlanNode]]:
    """Check source directives for cycles, depth, and file access.

    Returns (buildable_directives, error_children).
    """
    buildable: list[Directive] = []
    error_children: list[PlanNode] = []
    for d in (d for d in directives if d.source):
        error = _validate_source(d, depth, ancestors, context)
        if error:
            error_children.append(_error_node(d, [error]))
        else:
            buildable.append(d)
    return buildable, error_children


def _validate_source(
    directive: Directive,
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
) -> Status | None:
    """Check a single source directive for cycles, depth, and file access. Returns error or None."""
    if directive.source in ancestors:
        return Status(StatusLevel.ERROR, f"circular dependency detected: '{to_relative(directive.source)}'")
    if depth >= context.config.max_recursion:
        return Status(StatusLevel.ERROR, f"max recursion depth ({context.config.max_recursion}) reached")
    source_errors = context.file_cache.validate(directive.source)
    if source_errors:
        return source_errors[0]
    return None


def _validate_sourceless_directives(
    directives: list[Directive],
    context: EmbedmContext,
    plugin_config: PluginConfiguration,
) -> list[PlanNode]:
    """Call normalize_input for source-less directives that have a registered plugin."""
    nodes: list[PlanNode] = []
    for d in (d for d in directives if not d.source):
        plugin = context.plugin_registry.find_plugin_by_directive_type(d.type)
        if plugin is None:
            continue
        validate_result = plugin.normalize_input(d, "", plugin_config)
        if validate_result is not None and validate_result.errors:
            nodes.append(_error_node(d, validate_result.errors))
        else:
            node = PlanNode(directive=d, status=[], document=None, children=None)
            if validate_result is not None and validate_result.normalized_data is not None:
                node.normalized_data = validate_result.normalized_data
            nodes.append(node)
    return nodes


def _build_children(
    directives: list[Directive],
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
    plugin_config: PluginConfiguration,
) -> list[PlanNode]:
    """Recursively build child plan nodes for directives with sources."""
    return [_build_child(d, depth, ancestors, context, plugin_config) for d in directives if d.source]


def _build_child(
    directive: Directive,
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
    plugin_config: PluginConfiguration,
) -> PlanNode:
    """Build a single child plan node, loading content then delegating to _validate_and_plan."""
    source_content, load_errors = context.file_cache.get_file(directive.source)
    if load_errors or source_content is None:
        errors = load_errors or [Status(StatusLevel.ERROR, f"failed to load '{to_relative(directive.source)}'")]
        return _error_node(directive, errors)
    return _validate_and_plan(
        directive, source_content, depth + 1, ancestors | {directive.source}, context, plugin_config
    )


def _validate_and_plan(
    directive: Directive,
    content: str,
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
    plugin_config: PluginConfiguration,
) -> PlanNode:
    """Run normalize_input if a plugin is registered, then build a plan node."""
    plugin = context.plugin_registry.find_plugin_by_directive_type(directive.type)
    validate_result = plugin.normalize_input(directive, content, plugin_config) if plugin is not None else None
    if validate_result is not None and validate_result.errors:
        return _error_node(directive, validate_result.errors)
    node = create_plan(directive, content, depth, context, ancestors)
    if validate_result is not None and validate_result.normalized_data is not None:
        node.normalized_data = validate_result.normalized_data
    return node


def _error_node(directive: Directive, errors: list[Status]) -> PlanNode:
    """Create a PlanNode representing a failed plan step."""
    return PlanNode(directive=directive, status=errors, document=None, children=None)
