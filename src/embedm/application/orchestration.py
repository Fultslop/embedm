from __future__ import annotations

import sys
from pathlib import Path

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
        _process_directory(config, context)
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


def _process_directory(config: Configuration, context: EmbedmContext) -> None:
    """Expand directory input to .md files, process each, skipping embedded dependencies."""
    files = _expand_directory_input(config.input)
    if not files:
        present_errors(f"no .md files found in '{config.input}'")
        return

    base_dir = _extract_base_dir(config.input)
    embedded: set[str] = set()

    for file_path in files:
        resolved = str(Path(file_path).resolve())
        if resolved in embedded:
            continue

        plan_root = plan_file(file_path, context)

        # track all sources this file embeds so we skip them as standalone roots
        _collect_embedded_sources(plan_root, embedded)

        result = _compile_plan(plan_root, context)
        if result:
            _write_directory_output(file_path, base_dir, config, result)


def _expand_directory_input(input_path: str) -> list[str]:
    """Expand a directory or glob pattern to a sorted list of .md files."""
    if "**" in input_path:
        base = input_path.replace("/**", "").replace("**", ".")
        return sorted(str(p) for p in Path(base).rglob("*.md"))
    if "*" in input_path:
        base = input_path.replace("/*", "").replace("*", ".")
        return sorted(str(p) for p in Path(base).glob("*.md"))
    return sorted(str(p) for p in Path(input_path).glob("*.md"))


def _collect_embedded_sources(node: PlanNode, sources: set[str]) -> None:
    """Walk the plan tree and collect all embedded source paths."""
    for child in node.children or []:
        if child.directive.source:
            sources.add(str(Path(child.directive.source).resolve()))
        _collect_embedded_sources(child, sources)


def _compile_plan(plan_root: PlanNode, context: EmbedmContext) -> str:
    """Compile a plan tree into output with interactive error prompting."""
    if plan_root.document is None:
        present_errors(plan_root.status)
        return ""

    tree_errors = _collect_tree_errors(plan_root)
    if tree_errors:
        present_errors(tree_errors)
        has_fatal = any(s.level == StatusLevel.FATAL for s in tree_errors)
        if has_fatal or (not context.config.is_force_set and not prompt_continue()):
            return ""

    return _compile_plan_node(plan_root, context)


def _compile_plan_node(plan_root: PlanNode, context: EmbedmContext) -> str:
    """Compile a validated plan node via its plugin."""
    plugin = context.plugin_registry.find_plugin_by_directive_type(plan_root.directive.type)
    assert plugin is not None, (
        f"no plugin for directive type '{plan_root.directive.type}' — planner should have caught this"
    )
    return plugin.transform(plan_root, [], context.file_cache, context.plugin_registry)


def _extract_base_dir(input_path: str) -> Path:
    """Extract the base directory from a directory input or glob pattern."""
    cleaned = input_path.replace("/**", "").replace("/*", "").replace("**", ".").replace("*", ".")
    return Path(cleaned).resolve()


def _write_directory_output(
    file_path: str,
    base_dir: Path,
    config: Configuration,
    result: str,
) -> None:
    """Write a compiled file's output to the output directory (mirroring structure) or stdout."""
    if config.is_dry_run or not config.output_directory:
        present_result(result)
        return

    relative = Path(file_path).resolve().relative_to(base_dir)
    output_path = Path(config.output_directory) / relative
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")


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
    return _compile_plan(plan_root, context)


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
