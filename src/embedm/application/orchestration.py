from __future__ import annotations

import sys

from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_registry import PluginRegistry

from .cli import parse_command_line_arguments
from .config_loader import discover_config, generate_default_config, load_config_file
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

    if config.init_path is not None:
        _handle_init(config.init_path)
        return

    config, errors = _resolve_config(config)
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


def _handle_init(directory: str) -> None:
    """Generate a default config file and exit."""
    path, errors = generate_default_config(directory)
    if errors:
        present_errors(errors)
        sys.exit(1)
    present_result(f"created {path}\n")


def _resolve_config(config: Configuration) -> tuple[Configuration, list[Status]]:
    """Resolve configuration from file (explicit or auto-discovered) and merge with CLI config."""
    config_path = config.config_file or discover_config(config.input)
    if config_path is None:
        return config, []

    file_config, errors = load_config_file(config_path)
    if any(s.level == StatusLevel.ERROR for s in errors):
        return config, errors

    # merge: config file provides base values, CLI-only fields come from the parsed config
    return Configuration(
        input_mode=config.input_mode,
        input=config.input,
        output_file=config.output_file,
        output_directory=config.output_directory,
        max_file_size=file_config.max_file_size,
        max_recursion=file_config.max_recursion,
        max_memory=file_config.max_memory,
        max_embed_size=file_config.max_embed_size,
        root_directive_type=file_config.root_directive_type,
        plugin_sequence=file_config.plugin_sequence,
        is_force_set=config.is_force_set,
        is_dry_run=config.is_dry_run,
        config_file=config_path,
    ), errors


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
