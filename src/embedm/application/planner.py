import time
from pathlib import Path

from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.parsing.directive_parser import parse_yaml_embed_blocks
from embedm.plugins.plugin_configuration import PluginConfiguration

from .application_resources import str_resources
from .console import verbose_timing
from .embedm_context import EmbedmContext


def plan_content(content: str, context: EmbedmContext) -> PlanNode:
    """Create a plan for raw content, using cwd as the base directory."""
    source = str(Path.cwd() / "<stdin>")
    root_directive = Directive(type=context.config.root_directive_type, source=source)
    return create_plan(root_directive, content, 0, context)


def plan_file(file_name: str, context: EmbedmContext) -> PlanNode:
    """Create a plan for a file, using the configured root directive type."""
    resolved = str(Path(file_name).resolve())
    root_directive = Directive(type=context.config.root_directive_type, source=resolved)
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
    validation_errors, buildable, error_children = _validate_directives(
        directives,
        depth,
        ancestors,
        context,
        plugin_config,
    )
    all_errors.extend(validation_errors)

    # step 4: recurse into buildable source directives, include error children
    children = _build_children(buildable, depth, ancestors, context, plugin_config) + error_children

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
) -> tuple[list[Status], list[Directive], list[PlanNode]]:
    """Validate directives. Returns (all_errors, buildable_directives, error_children)."""
    errors: list[Status] = []
    buildable: list[Directive] = []
    error_children: list[PlanNode] = []

    for d in directives:
        plugin = context.plugin_registry.find_plugin_by_directive_type(d.type)
        if plugin is None:
            if context.config.is_verbose:
                available = ", ".join(sorted(p.directive_type for p in context.plugin_registry.lookup.values()))
                msg = str_resources.err_plan_no_plugin_verbose.format(directive_type=d.type, available=available)
            else:
                msg = str_resources.err_plan_no_plugin.format(directive_type=d.type)
            errors.append(Status(StatusLevel.ERROR, msg))
        else:
            t0 = time.perf_counter()
            errors.extend(plugin.validate_directive(d, plugin_config))
            if context.config.is_verbose:
                verbose_timing("validate_directive", d.type, d.source, time.perf_counter() - t0)

    valid_directives = (d for d in directives if d.source)

    for d in valid_directives:
        error = _validate_source(d, depth, ancestors, context)
        if error:
            error_children.append(_error_node(d, [error]))
        else:
            buildable.append(d)

    return errors, buildable, error_children


def _validate_source(
    directive: Directive,
    depth: int,
    ancestors: frozenset[str],
    context: EmbedmContext,
) -> Status | None:
    """Check a single source directive for cycles, depth, and file access. Returns error or None."""
    if directive.source in ancestors:
        return Status(StatusLevel.ERROR, f"circular dependency detected: '{directive.source}'")
    if depth >= context.config.max_recursion:
        return Status(StatusLevel.ERROR, f"max recursion depth ({context.config.max_recursion}) reached")
    source_errors = context.file_cache.validate(directive.source)
    if source_errors:
        return source_errors[0]
    return None


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
    """Build a single child plan node, running validate_input if a plugin is registered."""
    source_content, load_errors = context.file_cache.get_file(directive.source)
    if load_errors or source_content is None:
        errors = load_errors or [Status(StatusLevel.ERROR, f"failed to load '{directive.source}'")]
        return _error_node(directive, errors)

    plugin = context.plugin_registry.find_plugin_by_directive_type(directive.type)
    if plugin is not None:
        t0 = time.perf_counter()
        validate_result = plugin.validate_input(directive, source_content, plugin_config)
        if context.config.is_verbose:
            verbose_timing("validate_input", directive.type, directive.source, time.perf_counter() - t0)
    else:
        validate_result = None
    if validate_result is not None and validate_result.errors:
        return _error_node(directive, validate_result.errors)

    child = create_plan(directive, source_content, depth + 1, context, ancestors | {directive.source})
    if validate_result is not None and validate_result.artifact is not None:
        child.artifact = validate_result.artifact
    return child


def _error_node(directive: Directive, errors: list[Status]) -> PlanNode:
    """Create a PlanNode representing a failed plan step."""
    return PlanNode(directive=directive, status=errors, document=None, children=None)
