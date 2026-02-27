from __future__ import annotations

import sys
from pathlib import Path

from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_context import PluginContext
from embedm.plugins.plugin_registry import PluginRegistry

from .application_events import NodeCompiled
from .configuration import Configuration
from .console import ContinueChoice, prompt_continue
from .embedm_context import EmbedmContext
from .output_util import present_errors
from .plan_tree import collect_tree_errors, count_nodes


def compile_plan(plan_root: PlanNode, context: EmbedmContext, compiled_dir: str = "") -> str:
    """Compile a plan tree into output with interactive error prompting."""
    if plan_root.document is None:
        _emit_errors(plan_root.status, context)
        return ""

    tree_errors = collect_tree_errors(plan_root)
    if tree_errors:
        _emit_errors(tree_errors, context)
        has_fatal = any(s.level == StatusLevel.FATAL for s in tree_errors)
        if has_fatal:
            return ""
        if not context.accept_all:
            choice = prompt_continue()
            if choice == ContinueChoice.EXIT:
                sys.exit(1)
            if choice == ContinueChoice.NO:
                return ""
            if choice == ContinueChoice.ALWAYS:
                context.accept_all = True

    return _compile_plan_node(plan_root, context, compiled_dir)


def _compile_plan_node(plan_root: PlanNode, context: EmbedmContext, compiled_dir: str = "") -> str:
    """Compile a validated plan node via its plugin."""
    plugin = context.plugin_registry.find_plugin_by_directive_type(plan_root.directive.type)
    if plugin is None:
        return ""
    plugin_config = PluginConfiguration(
        max_embed_size=context.config.max_embed_size,
        max_recursion=context.config.max_recursion,
        compiled_dir=compiled_dir,
        plugin_sequence=build_directive_sequence(context.config.plugin_sequence, context.plugin_registry),
        plugin_settings=context.config.plugin_configuration,
    )
    node_total = count_nodes(plan_root)
    tracker: dict[str, int] = {"index": 0, "total": node_total}
    file_path = plan_root.directive.source
    events = context.events

    def _on_node_compiled(node_index: int, node_count: int, elapsed: float) -> None:
        if events is not None:
            events.emit(
                NodeCompiled(file_path=file_path, node_index=node_index, node_count=node_count, elapsed=elapsed)
            )

    result = plugin.transform(
        plan_root,
        [],
        PluginContext(
            context.file_cache,
            context.plugin_registry,
            plugin_config,
            events=context.events,
            plugin_name=plugin.name,
            file_path=file_path,
            _compile_tracker=tracker,
            _on_node_compiled=_on_node_compiled,
        ),
    )
    return result


def build_directive_sequence(plugin_sequence: list[str], registry: PluginRegistry) -> tuple[str, ...]:
    """Return directive types ordered by plugin_sequence module order.

    Any loaded plugins whose module is not in plugin_sequence are appended at the end.
    """
    result: list[str] = []
    covered: set[str] = set()
    for module in plugin_sequence:
        for plugin in registry.lookup.values():
            if plugin.__class__.__module__ == module and plugin.directive_type not in covered:
                result.append(plugin.directive_type)
                covered.add(plugin.directive_type)
                break
    for plugin in registry.lookup.values():
        if plugin.directive_type not in covered:
            result.append(plugin.directive_type)
            covered.add(plugin.directive_type)
    return tuple(result)


def output_file_compiled_dir(output_file: str | None) -> str:
    """Return the directory of the output file, or empty string if writing to stdout."""
    return str(Path(output_file).resolve().parent) if output_file else ""


def dir_mode_compiled_dir(file_path: str, base_dir: Path, config: Configuration) -> str:
    """Return the compiled output directory for a file in directory mode."""
    if not config.output_directory:
        return ""
    try:
        relative = Path(file_path).resolve().relative_to(base_dir)
        return str((Path(config.output_directory) / relative).parent.resolve())
    except ValueError:
        return ""


def _emit_errors(errors: list[Status], context: EmbedmContext) -> None:
    """Present errors unless suppressed (accept-all at verbosity < 2)."""
    if context.config.verbosity >= 2 or not context.accept_all:
        present_errors(errors)
