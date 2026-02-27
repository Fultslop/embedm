from __future__ import annotations

import sys
import time
from importlib.metadata import version as pkg_version
from pathlib import Path

from embedm.application.application_events import FileProcessed, PluginsLoaded, SessionComplete, SessionStarted
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.events import EventDispatcher
from embedm.infrastructure.file_cache import FileCache
from embedm.infrastructure.file_util import apply_line_endings, expand_directory_input, extract_base_dir
from embedm.plugins.plugin_registry import PluginRegistry

from .application_resources import str_resources as app_resources
from .cli import parse_command_line_arguments
from .compiler import compile_plan, dir_mode_compiled_dir, output_file_compiled_dir
from .config_loader import discover_config, generate_default_config, load_config_file
from .configuration import Configuration, InputMode
from .console import RunSummary
from .embedm_context import EmbedmContext
from .legacy_renderer import LegacyRenderer
from .output_util import present_errors, present_plugin_list, present_result, present_verify_status
from .plan_tree import collect_embedded_sources, tree_has_level
from .planner import plan_content, plan_file
from .plugin_diagnostics import PluginDiagnostics
from .verification import VerifyStatus, verify_file_output


def main() -> None:
    """Entry point for the embedm CLI."""
    start_time = time.perf_counter()

    config, errors = parse_command_line_arguments()
    _exit_if_errors(errors)

    if config.init_path is not None:
        _handle_init(config.init_path)
        return

    dispatcher = EventDispatcher()
    LegacyRenderer(config).subscribe(dispatcher)

    config, errors = _resolve_config(config)
    _exit_if_errors(errors)

    dispatcher.emit(
        SessionStarted(
            version=pkg_version("embedm"),
            config_source=config.config_file or "DEFAULT",
            input_type=config.input_mode.value,
            output_type=_format_output_label(config),
        )
    )

    if config.plugin_list:
        _handle_plugin_list(config)
        return

    plugin_registry, load_errors = _load_plugins(config)
    _handle_plugin_load_errors(load_errors)

    diagnostics = PluginDiagnostics().check(plugin_registry, config)
    dispatcher.emit(
        PluginsLoaded(
            discovered=len(plugin_registry.discovered),
            loaded=plugin_registry.count,
            errors=[e.description for e in load_errors],
            warnings=[d.description for d in diagnostics],
        )
    )

    context = _build_context(config, plugin_registry, dispatcher)
    summary = RunSummary(output_target=_format_output_label(config))

    _dispatch_input(config, context, summary)

    summary.elapsed_s = time.perf_counter() - start_time
    dispatcher.emit(
        SessionComplete(
            ok_count=summary.ok_count,
            error_count=summary.error_count,
            total_elapsed=summary.elapsed_s,
            files_written=summary.files_written,
            output_target=summary.output_target,
            warning_count=summary.warning_count,
            is_verify=summary.is_verify,
            up_to_date_count=summary.up_to_date_count,
            stale_count=summary.stale_count,
        )
    )
    _exit_on_run_failure(config, summary)


def _exit_if_errors(errors: list[Status]) -> None:
    """Print errors and exit if the list is non-empty."""
    if errors:
        present_errors(errors)
        sys.exit(1)


def _exit_on_run_failure(config: Configuration, summary: RunSummary) -> None:
    """Exit with failure if the run produced errors or stale files."""
    if summary.error_count > 0 or (config.is_verify and summary.stale_count > 0):
        sys.exit(1)


def _handle_plugin_load_errors(load_errors: list[Status]) -> None:
    """Present plugin load errors; exits if any are fatal."""
    fatal = [e for e in load_errors if e.level == StatusLevel.FATAL]
    if fatal:
        present_errors(fatal)
        present_errors(app_resources.err_fatal_plugins_cannot_start)
        sys.exit(1)
    if load_errors:
        present_errors(load_errors)


def _handle_init(directory: str) -> None:
    """Generate a default config file and exit."""
    path, errors = generate_default_config(directory)
    if errors:
        present_errors(errors)
        sys.exit(1)
    present_result(f"created {path}\n")


def _handle_plugin_list(config: Configuration) -> None:
    """Load plugins, run diagnostics, print the report, and exit."""
    registry = PluginRegistry()
    load_errors = registry.load_plugins(enabled_modules=set(config.plugin_sequence))
    diagnostics = PluginDiagnostics().check(registry, config)
    present_plugin_list(registry, load_errors + diagnostics)
    has_errors = any(e.level in (StatusLevel.ERROR, StatusLevel.FATAL) for e in load_errors)
    sys.exit(1 if has_errors else 0)


def _resolve_config(config: Configuration) -> tuple[Configuration, list[Status]]:
    """Resolve configuration from file (explicit or auto-discovered) and merge with CLI config."""
    config_path = config.config_file or discover_config(config.input)
    if config_path is None:
        return config, []

    file_config, errors = load_config_file(config_path)
    if any(s.level == StatusLevel.ERROR for s in errors):
        return config, errors

    return Configuration.merge(config, file_config, config_path), errors


def _dispatch_input(config: Configuration, context: EmbedmContext, summary: RunSummary) -> None:
    """Route to the appropriate processing function based on input mode."""
    if config.input_mode == InputMode.FILE:
        plan_root = plan_file(config.input, context)
        _process_single_input(plan_root, config, context, summary)
    elif config.input_mode == InputMode.DIRECTORY:
        _process_directory(config, context, summary)
    elif config.input_mode == InputMode.STDIN:
        plan_root = plan_content(config.input, context)
        _process_single_input(plan_root, config, context, summary)


def _process_directory(config: Configuration, context: EmbedmContext, summary: RunSummary) -> None:
    """Expand directory input to .md files, process each, skipping embedded dependencies."""
    files = expand_directory_input(config.input, "*.md")
    if not files:
        present_errors(f"no .md files found in '{config.input}'")
        return

    base_dir = extract_base_dir(config.input)
    embedded: set[str] = set()

    for i, file_path in enumerate(files):
        _process_directory_file(file_path, i, len(files), base_dir, config, context, summary, embedded)


def _process_directory_file(
    file_path: str,
    index: int,
    total: int,
    base_dir: Path,
    config: Configuration,
    context: EmbedmContext,
    summary: RunSummary,
    embedded: set[str],
) -> None:
    """Process a single file within directory mode, skipping embedded dependencies."""
    resolved = str(Path(file_path).resolve())
    if resolved in embedded:
        return

    plan_root = plan_file(file_path, context)

    # track all sources this file embeds so we skip them as standalone roots
    embedded.update(collect_embedded_sources(plan_root, embed_type=config.root_directive_type))

    compiled_dir = dir_mode_compiled_dir(file_path, base_dir, config)
    result = compile_plan(plan_root, context, compiled_dir)
    if result and config.is_verify and config.output_directory:
        relative = Path(file_path).resolve().relative_to(base_dir)
        output_path = str((Path(config.output_directory) / relative).resolve())
        vstatus = verify_file_output(result, output_path, config)
        present_verify_status(vstatus.value, output_path)
        _update_summary(summary, plan_root, wrote=False, verify_status=vstatus)
    else:
        if result:
            _write_directory_output(file_path, base_dir, config, result)
        _update_summary(summary, plan_root, wrote=bool(result))

    context.events.emit(
        FileProcessed(file_path=file_path, status_label=_plan_status_label(plan_root), index=index, total=total)
    )


def _process_single_input(
    plan_root: PlanNode,
    config: Configuration,
    context: EmbedmContext,
    summary: RunSummary,
) -> None:
    """Compile and write a single plan (FILE or STDIN mode), updating the summary."""
    compiled_dir = output_file_compiled_dir(config.output_file)
    result = compile_plan(plan_root, context, compiled_dir)

    if config.is_verify and result and config.output_file:
        output_path = str(Path(config.output_file).resolve())
        vstatus = verify_file_output(result, output_path, config)
        present_verify_status(vstatus.value, output_path)
        _update_summary(summary, plan_root, wrote=False, verify_status=vstatus)
    else:
        _write_output(result, config)
        _update_summary(summary, plan_root, wrote=bool(result))


def _validate_plugin_config_schemas(config: Configuration, registry: PluginRegistry) -> list[Status]:
    """Validate per-plugin config sections against each plugin's declared schema."""
    errors: list[Status] = []
    for module, settings in config.plugin_configuration.items():
        plugin = next((p for p in registry.lookup.values() if p.__class__.__module__ == module), None)
        if plugin is None:
            errors.append(
                Status(StatusLevel.WARNING, app_resources.warn_plugin_config_unknown_module.format(module=module))
            )
            continue

        schema = plugin.get_plugin_config_schema()
        for key, value in settings.items():
            if schema is None or key not in schema:
                if config.verbosity >= 3:
                    errors.append(
                        Status(
                            StatusLevel.WARNING,
                            app_resources.warn_plugin_config_unknown_key.format(module=module, key=key),
                        )
                    )
                continue
            if not isinstance(value, schema[key]):
                errors.append(
                    Status(
                        StatusLevel.ERROR,
                        app_resources.err_plugin_config_type_mismatch.format(
                            module=module, key=key, expected=schema[key].__name__, got=type(value).__name__
                        ),
                    )
                )

        errors.extend(plugin.validate_plugin_config(settings))

    return errors


def _load_plugins(config: Configuration) -> tuple[PluginRegistry, list[Status]]:
    """Create and populate the plugin registry, validating plugin configuration schemas."""
    plugin_registry = PluginRegistry()
    errors = plugin_registry.load_plugins(enabled_modules=set(config.plugin_sequence))
    errors.extend(_validate_plugin_config_schemas(config, plugin_registry))
    return plugin_registry, errors


def _build_context(
    config: Configuration, plugin_registry: PluginRegistry, dispatcher: EventDispatcher
) -> EmbedmContext:
    """Build the runtime context from configuration and a loaded plugin registry."""
    file_cache = FileCache(
        config.max_file_size, config.max_memory, ["./**"], max_embed_size=config.max_embed_size, events=dispatcher
    )
    return EmbedmContext(config, file_cache, plugin_registry, accept_all=config.is_accept_all, events=dispatcher)


def _format_output_label(config: Configuration) -> str:
    """Return a human-readable output target label for the summary line."""
    if config.output_file:
        return str(Path(config.output_file).resolve())
    if config.output_directory:
        return str(Path(config.output_directory).resolve())
    return "stdout"


def _write_directory_output(
    file_path: str,
    base_dir: Path,
    config: Configuration,
    result: str,
) -> str | None:
    """Write a compiled file's output to the output directory (mirroring structure) or stdout.

    Returns the path written to, or None if written to stdout.
    """
    content = apply_line_endings(result, config.line_endings)

    if config.is_dry_run or not config.output_directory:
        present_result(content)
        return None

    relative = Path(file_path).resolve().relative_to(base_dir)
    output_path = Path(config.output_directory) / relative
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return str(output_path.resolve())


def _write_output(result: str, config: Configuration) -> str | None:
    """Write compilation result to the configured destination.

    Returns the path written to, or None if written to stdout or result was empty.
    """
    if not result:
        return None

    content = apply_line_endings(result, config.line_endings)

    if config.is_dry_run:
        present_result(content)
        return None

    if config.output_file:
        with open(config.output_file, "w", encoding="utf-8") as f:
            f.write(content)
        return str(Path(config.output_file).resolve())

    present_result(content)
    return None


def _plan_status_label(plan_root: PlanNode) -> str:
    """Return a single status label string for the worst status in the plan root."""
    statuses = plan_root.status
    if any(s.level == StatusLevel.FATAL for s in statuses):
        return "FATAL"
    if any(s.level == StatusLevel.ERROR for s in statuses):
        return "ERROR"
    if any(s.level == StatusLevel.WARNING for s in statuses):
        return "WARN"
    return "OK"


def _update_summary(
    summary: RunSummary,
    plan_root: PlanNode,
    wrote: bool,
    verify_status: VerifyStatus | None = None,
) -> None:
    """Update the run summary from a completed plan."""
    has_error = tree_has_level(plan_root, (StatusLevel.ERROR, StatusLevel.FATAL))
    has_warning = tree_has_level(plan_root, (StatusLevel.WARNING,))

    if verify_status is not None:
        summary.is_verify = True
        if verify_status == VerifyStatus.UP_TO_DATE:
            summary.up_to_date_count += 1
        else:
            summary.stale_count += 1
    elif wrote:
        summary.files_written += 1

    if has_error:
        summary.error_count += 1
    elif has_warning:
        summary.warning_count += 1
    else:
        summary.ok_count += 1
