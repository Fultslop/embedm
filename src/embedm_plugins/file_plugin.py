from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.parsing.extraction import DEFAULT_REGION_END, DEFAULT_REGION_START, is_valid_line_range
from embedm.parsing.symbol_parser import get_language_config
from embedm.plugins.directive_options import get_option
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm_plugins.file_resources import render_error_note, str_resources
from embedm_plugins.file_transformer import FileParams, FileTransformer
from embedm_plugins.line_transformer import LineParams, LineTransformer
from embedm_plugins.region_transformer import RegionParams, RegionTransformer
from embedm_plugins.symbol_transformer import SymbolParams, SymbolTransformer

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry

_EXTRACTION_OPTIONS = ("region", "lines", "symbol")
_MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def _validate_lines_option(line_range: str | None) -> Status | None:
    if line_range is not None and not is_valid_line_range(line_range):
        return Status(StatusLevel.ERROR, str_resources.err_file_invalid_line_range.format(range=line_range))
    return None


def _validate_symbol_option(source: str, symbol: str | None) -> Status | None:
    if symbol and get_language_config(source) is None:
        ext = Path(source).suffix
        return Status(StatusLevel.ERROR, str_resources.err_file_symbol_unsupported_ext.format(ext=ext))
    return None


class FilePlugin(PluginBase):
    name = "file plugin"
    api_version = 1
    directive_type = "file"

    def get_plugin_config_schema(self) -> dict[str, type]:
        """Return the config keys accepted by the file plugin."""
        return {"region_start": str, "region_end": str}

    def validate_plugin_config(self, settings: dict[str, Any]) -> list[Status]:
        """Validate that region marker templates contain {tag}."""
        errors: list[Status] = []
        for key in ("region_start", "region_end"):
            value = settings.get(key)
            if value is not None and "{tag}" not in value:
                errors.append(Status(StatusLevel.ERROR, f"file_plugin config '{key}' must contain '{{tag}}'"))
        return errors

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        if not directive.source:
            return [Status(StatusLevel.ERROR, "'file' directive requires a source")]

        errors: list[Status] = []

        active = [k for k in _EXTRACTION_OPTIONS if directive.options.get(k)]
        if len(active) > 1:
            errors.append(Status(StatusLevel.ERROR, str_resources.err_file_exclusive_options))

        for err in [
            _validate_lines_option(directive.options.get("lines")),
            _validate_symbol_option(directive.source, directive.options.get("symbol")),
        ]:
            if err is not None:
                errors.append(err)

        return errors

    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        file_cache: FileCache | None = None,
        plugin_registry: PluginRegistry | None = None,
        plugin_config: PluginConfiguration | None = None,
    ) -> str:
        assert file_cache is not None, "file_cache is required — orchestration must provide it"
        assert plugin_registry is not None, "plugin_registry is required — orchestration must provide it"

        if plan_node.document is None:
            return ""

        compiled = FileTransformer().execute(
            FileParams(
                plan_node=plan_node,
                parent_document=parent_document,
                file_cache=file_cache,
                plugin_registry=plugin_registry,
                plugin_config=plugin_config,
            )
        )

        source_path = plan_node.directive.source
        region = plan_node.directive.options.get("region")
        line_range = plan_node.directive.options.get("lines")
        symbol = plan_node.directive.options.get("symbol")

        settings = plugin_config.plugin_settings.get(self.__class__.__module__, {}) if plugin_config else {}
        region_start = settings.get("region_start", DEFAULT_REGION_START)
        region_end = settings.get("region_end", DEFAULT_REGION_END)

        content = _apply_extraction(compiled, source_path, region, line_range, symbol, region_start, region_end)
        if isinstance(content, Status):
            return render_error_note([content.description])

        title = plan_node.directive.options.get("title")
        show_link = get_option(plan_node.directive, "link", bool, False)
        show_line_range = get_option(plan_node.directive, "line_numbers_range", bool, False)
        compiled_dir = plugin_config.compiled_dir if plugin_config else ""
        header = _build_header(source_path, compiled_dir, title, show_line_range, show_link, line_range)

        is_markdown = Path(source_path).suffix.lower() in _MARKDOWN_EXTENSIONS
        if not is_markdown:
            ext = Path(source_path).suffix.lstrip(".") or "text"
            return f"{header}```{ext}\n{content.rstrip()}\n```"

        return f"{header}{content}"


def _apply_region(
    compiled: str,
    region: str,
    source_path: str,
    region_start_template: str = DEFAULT_REGION_START,
    region_end_template: str = DEFAULT_REGION_END,
) -> str | Status:
    result = RegionTransformer().execute(
        RegionParams(
            content=compiled,
            region_name=region,
            region_start_template=region_start_template,
            region_end_template=region_end_template,
        )
    )
    if result is None:
        msg = str_resources.err_file_region_not_found.format(region=region, source=source_path)
        return Status(StatusLevel.ERROR, msg)
    return result


def _apply_lines(compiled: str, line_range: str) -> str | Status:
    result = LineTransformer().execute(LineParams(content=compiled, line_range=line_range))
    if result is None:
        return Status(StatusLevel.ERROR, str_resources.err_file_invalid_line_range.format(range=line_range))
    return result


def _apply_symbol(compiled: str, symbol: str, source_path: str) -> str | Status:
    config = get_language_config(source_path)
    if config is None:
        ext = Path(source_path).suffix
        return Status(StatusLevel.ERROR, str_resources.err_file_symbol_unsupported_ext.format(ext=ext))
    result = SymbolTransformer().execute(SymbolParams(content=compiled, symbol_name=symbol, config=config))
    if result is None:
        msg = str_resources.err_file_symbol_not_found.format(symbol=symbol, source=source_path)
        return Status(StatusLevel.ERROR, msg)
    return result


def _build_header(
    source_path: str,
    compiled_dir: str,
    title: str | None,
    show_line_range: bool,
    show_link: bool,
    line_range: str | None,
) -> str:
    """Build an optional header line to prepend above the code block.

    Elements are emitted in order: title, line_numbers_range, link.
    Returns an empty string if no elements are active.
    """
    parts: list[str] = []
    if title:
        parts.append(f'**"{title}"**')
    if show_line_range and line_range:
        parts.append(f"(lines {line_range})")
    if show_link:
        filename = Path(source_path).name
        link_target = _relative_link_path(source_path, compiled_dir)
        parts.append(f"[link {filename}]({link_target})")
    return "> " + " ".join(parts) + "\n" if parts else ""


def _relative_link_path(source_path: str, compiled_dir: str) -> str:
    """Return the path from compiled_dir to source_path using POSIX separators.

    Falls back to the filename if compiled_dir is unset or on a different drive.
    """
    if not compiled_dir:
        return Path(source_path).name
    try:
        return Path(os.path.relpath(source_path, compiled_dir)).as_posix()
    except ValueError:
        return Path(source_path).name


def _apply_extraction(
    compiled: str,
    source_path: str,
    region: str | None,
    line_range: str | None,
    symbol: str | None,
    region_start_template: str = DEFAULT_REGION_START,
    region_end_template: str = DEFAULT_REGION_END,
) -> str | Status:
    """Apply the appropriate extraction step and return the result or an error Status."""
    if region:
        return _apply_region(compiled, region, source_path, region_start_template, region_end_template)
    if line_range:
        return _apply_lines(compiled, line_range)
    if symbol:
        return _apply_symbol(compiled, symbol, source_path)
    return compiled
