from __future__ import annotations

import sys

from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_registry import PluginRegistry

from .cli import parse_command_line_arguments
from .configuration import Configuration, InputMode
from .console import present_errors, present_result, present_title, prompt_continue
from .embedm_context import EmbedmContext
from .planner import plan_file


def main() -> None:
    """Entry point for the embedm CLI."""
    present_title()

    config, errors = parse_command_line_arguments()
    if errors:
        present_errors(errors)
        sys.exit(1)

    context = _build_context(config)

    if config.input_mode == InputMode.FILE:
        result = _process_file(config.input, context)
        _write_output(result, config)
    elif config.input_mode == InputMode.DIRECTORY:
        # TODO: expand directory into file list and process each
        present_errors("directory mode not yet implemented")
    elif config.input_mode == InputMode.STDIN:
        # TODO: handle stdin content
        present_errors("stdin mode not yet implemented")


def _build_context(config: Configuration) -> EmbedmContext:
    """Build the runtime context from configuration."""
    file_cache = FileCache(config.max_file_size, config.max_memory, ["./**"])
    plugin_registry = PluginRegistry()
    # TODO: filter by config.plugin_sequence
    plugin_registry.load_plugins()
    return EmbedmContext(config, file_cache, plugin_registry)


def _process_file(file_name: str, context: EmbedmContext) -> str:
    """Plan and compile a single input file."""
    plan_root = plan_file(file_name, context)

    # Root file couldn't be loaded — nothing to compile
    if plan_root.document is None:
        present_errors(plan_root.status)
        return ""

    # Collect all errors across the plan tree and let the user decide
    tree_errors = _collect_tree_errors(plan_root)
    if tree_errors:
        present_errors(tree_errors)
        has_fatal = any(s.level == StatusLevel.FATAL for s in tree_errors)
        if has_fatal or (not context.config.is_force_set and not prompt_continue()):
            return ""

    plugin = context.plugin_registry.find_plugin_by_directive_type(plan_root.directive.type)
    assert plugin is not None, (
        f"no plugin for directive type '{plan_root.directive.type}' — planner should have caught this"
    )

    return plugin.transform(plan_root, [], context.file_cache, context.plugin_registry)


def _collect_tree_errors(node: PlanNode) -> list[Status]:
    """Walk the plan tree and collect all error/fatal statuses."""
    errors = [s for s in node.status if s.level in (StatusLevel.ERROR, StatusLevel.FATAL)]
    for child in node.children or []:
        errors.extend(_collect_tree_errors(child))
    return errors


def _write_output(result: str, config: Configuration) -> None:
    """Write compilation result to the configured destination."""
    if not result:
        return

    if config.is_dry_run:
        present_result(result)
        return

    if config.output_file:
        with open(config.output_file, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        present_result(result)
