from __future__ import annotations

import sys
from pathlib import Path

from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_registry import PluginRegistry

from .cli import parse_command_line_arguments
from .config_loader import discover_config, generate_default_config, load_config_file
from .configuration import Configuration, InputMode
from .console import (
    ContinueChoice,
    RunSummary,
    make_cache_event_handler,
    present_errors,
    present_result,
    present_run_hint,
    present_title,
    prompt_continue,
    verbose_config,
    verbose_output_path,
    verbose_plan_tree,
    verbose_plugins,
    verbose_section,
    verbose_summary,
)
from .embedm_context import EmbedmContext
from .planner import plan_content, plan_file


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

    context, load_errors = _build_context(config)
    if load_errors:
        present_errors(load_errors)

    _emit_verbose_start(config, context)
    summary = RunSummary(output_target=_output_target(config))

    if config.input_mode == InputMode.FILE:
        plan_root = plan_file(config.input, context)
        _process_single_input(plan_root, config.input, config, context, summary)
    elif config.input_mode == InputMode.DIRECTORY:
        _process_directory(config, context, summary)
    elif config.input_mode == InputMode.STDIN:
        plan_root = plan_content(config.input, context)
        _process_single_input(plan_root, "<stdin>", config, context, summary)

    _emit_verbose_end(config, summary)


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
        plugin_configuration=file_config.plugin_configuration,
        is_accept_all=config.is_accept_all,
        is_dry_run=config.is_dry_run,
        is_verbose=config.is_verbose,
        config_file=config_path,
    ), errors


def _process_directory(config: Configuration, context: EmbedmContext, summary: RunSummary) -> None:
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

        if config.is_verbose:
            verbose_section(f"planning: {file_path}")
            verbose_plan_tree(plan_root)

        # track all sources this file embeds so we skip them as standalone roots
        _collect_embedded_sources(plan_root, embedded)

        compiled_dir = _dir_mode_compiled_dir(file_path, base_dir, config)
        result = _compile_plan(plan_root, context, compiled_dir)
        if result:
            output_path = _write_directory_output(file_path, base_dir, config, result)
            if output_path and config.is_verbose:
                verbose_output_path(output_path)
        _update_summary(summary, plan_root, wrote=bool(result))


def _expand_directory_input(input_path: str) -> list[str]:
    """Expand a directory or glob pattern to a sorted list of .md files."""
    if "**" in input_path:
        return sorted(str(p) for p in _glob_base(input_path).rglob("*.md"))
    if "*" in input_path:
        return sorted(str(p) for p in _glob_base(input_path).glob("*.md"))
    return sorted(str(p) for p in Path(input_path).glob("*.md"))


def _collect_embedded_sources(node: PlanNode, sources: set[str]) -> None:
    """Walk the plan tree and collect all embedded source paths."""
    for child in node.children or []:
        if child.directive.source:
            sources.add(str(Path(child.directive.source).resolve()))
        _collect_embedded_sources(child, sources)


def _compile_plan(plan_root: PlanNode, context: EmbedmContext, compiled_dir: str = "") -> str:
    """Compile a plan tree into output with interactive error prompting."""
    if plan_root.document is None:
        present_errors(plan_root.status)
        return ""

    tree_errors = _collect_tree_errors(plan_root)
    if tree_errors:
        present_errors(tree_errors)
        has_fatal = any(s.level == StatusLevel.FATAL for s in tree_errors)
        if has_fatal:
            return ""
        if not context.accept_all:
            choice = prompt_continue()
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
        plugin_sequence=_build_directive_sequence(context.config.plugin_sequence, context.plugin_registry),
        plugin_settings=context.config.plugin_configuration,
    )
    return plugin.transform(plan_root, [], context.file_cache, context.plugin_registry, plugin_config)


def _build_directive_sequence(plugin_sequence: list[str], registry: PluginRegistry) -> tuple[str, ...]:
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


def _glob_base(pattern: str) -> Path:
    """Return the directory prefix of a glob pattern: all parts before the first wildcard."""
    base: list[str] = []
    for part in Path(pattern).parts:
        if "*" in part:
            break
        base.append(part)
    return Path(*base) if base else Path(".")


def _extract_base_dir(input_path: str) -> Path:
    """Extract the base directory from a directory input or glob pattern."""
    return _glob_base(input_path).resolve() if "*" in input_path else Path(input_path).resolve()


def _write_directory_output(
    file_path: str,
    base_dir: Path,
    config: Configuration,
    result: str,
) -> str | None:
    """Write a compiled file's output to the output directory (mirroring structure) or stdout.

    Returns the path written to, or None if written to stdout.
    """
    if config.is_dry_run or not config.output_directory:
        present_result(result)
        return None

    relative = Path(file_path).resolve().relative_to(base_dir)
    output_path = Path(config.output_directory) / relative
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    return str(output_path.resolve())


def _emit_verbose_start(config: Configuration, context: EmbedmContext) -> None:
    """Emit the configuration and plugin discovery sections when verbose is on."""
    if config.is_verbose:
        verbose_section("configuration")
        verbose_config(config)
        verbose_section("plugins")
        verbose_plugins(context.plugin_registry, config)


def _emit_verbose_end(config: Configuration, summary: RunSummary) -> None:
    """Emit the summary section (verbose) or the error hint (non-verbose with errors)."""
    if config.is_verbose:
        verbose_section("summary")
        verbose_summary(summary)
    elif summary.error_count > 0:
        present_run_hint(summary)


def _process_single_input(
    plan_root: PlanNode,
    source_label: str,
    config: Configuration,
    context: EmbedmContext,
    summary: RunSummary,
) -> None:
    """Compile and write a single plan (FILE or STDIN mode), updating the summary."""
    if config.is_verbose:
        verbose_section(f"planning: {source_label}")
        verbose_plan_tree(plan_root)
    compiled_dir = _output_file_compiled_dir(config.output_file)
    result = _compile_plan(plan_root, context, compiled_dir)
    output_path = _write_output(result, config)
    if output_path and config.is_verbose:
        verbose_section("output")
        verbose_output_path(output_path)
    _update_summary(summary, plan_root, wrote=bool(result))


def _validate_plugin_configs(config: Configuration, registry: PluginRegistry) -> list[Status]:
    """Validate per-plugin config sections against each plugin's declared schema."""
    errors: list[Status] = []
    for module, settings in config.plugin_configuration.items():
        plugin = next((p for p in registry.lookup.values() if p.__class__.__module__ == module), None)
        if plugin is None:
            errors.append(Status(StatusLevel.WARNING, f"plugin_configuration: unknown plugin module '{module}'"))
            continue

        schema = plugin.get_plugin_config_schema()
        for key, value in settings.items():
            if schema is None or key not in schema:
                if config.is_verbose:
                    errors.append(Status(StatusLevel.WARNING, f"plugin_configuration['{module}']: unknown key '{key}'"))
                continue
            if not isinstance(value, schema[key]):
                errors.append(
                    Status(
                        StatusLevel.ERROR,
                        f"plugin_configuration['{module}']['{key}'] must be {schema[key].__name__},"
                        f" got {type(value).__name__}",
                    )
                )

        errors.extend(plugin.validate_plugin_config(settings))

    return errors


def _build_context(config: Configuration) -> tuple[EmbedmContext, list[Status]]:
    """Build the runtime context from configuration."""
    on_event = make_cache_event_handler() if config.is_verbose else None
    file_cache = FileCache(
        config.max_file_size, config.max_memory, ["./**"], max_embed_size=config.max_embed_size, on_event=on_event
    )
    plugin_registry = PluginRegistry()
    errors = plugin_registry.load_plugins(enabled_modules=set(config.plugin_sequence))
    errors.extend(_validate_plugin_configs(config, plugin_registry))
    return EmbedmContext(config, file_cache, plugin_registry, accept_all=config.is_accept_all), errors


def _output_file_compiled_dir(output_file: str | None) -> str:
    """Return the directory of the output file, or empty string if writing to stdout."""
    return str(Path(output_file).resolve().parent) if output_file else ""


def _dir_mode_compiled_dir(file_path: str, base_dir: Path, config: Configuration) -> str:
    """Return the compiled output directory for a file in directory mode."""
    if not config.output_directory:
        return ""
    try:
        relative = Path(file_path).resolve().relative_to(base_dir)
        return str((Path(config.output_directory) / relative).parent.resolve())
    except ValueError:
        return ""


def _collect_tree_errors(node: PlanNode) -> list[Status]:
    """Walk the plan tree and collect all error/fatal statuses."""
    errors = [s for s in node.status if s.level in (StatusLevel.ERROR, StatusLevel.FATAL)]
    for child in node.children or []:
        errors.extend(_collect_tree_errors(child))
    return errors


def _write_output(result: str, config: Configuration) -> str | None:
    """Write compilation result to the configured destination.

    Returns the path written to, or None if written to stdout or result was empty.
    """
    if not result:
        return None

    if config.is_dry_run:
        present_result(result)
        return None

    if config.output_file:
        with open(config.output_file, "w", encoding="utf-8") as f:
            f.write(result)
        return str(Path(config.output_file).resolve())

    present_result(result)
    return None


def _output_target(config: Configuration) -> str:
    """Return a human-readable output target label for the summary line."""
    if config.output_file:
        return str(Path(config.output_file).resolve())
    if config.output_directory:
        return str(Path(config.output_directory).resolve())
    return "stdout"


def _update_summary(summary: RunSummary, plan_root: PlanNode, wrote: bool) -> None:
    """Update the run summary from a completed plan."""
    has_error = _tree_has_level(plan_root, (StatusLevel.ERROR, StatusLevel.FATAL))
    has_warning = _tree_has_level(plan_root, (StatusLevel.WARNING,))

    if wrote:
        summary.files_written += 1

    if has_error:
        summary.error_count += 1
    elif has_warning:
        summary.warning_count += 1
    else:
        summary.ok_count += 1


def _tree_has_level(node: PlanNode, levels: tuple[StatusLevel, ...]) -> bool:
    """Return True if the plan tree contains any status at one of the given levels."""
    if any(s.level in levels for s in node.status):
        return True
    return any(_tree_has_level(child, levels) for child in node.children or [])
