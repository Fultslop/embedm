from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.parsing.extraction import is_valid_line_range
from embedm.parsing.symbol_parser import get_language_config
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm_plugins.file_transformer import FileParams, FileTransformer
from embedm_plugins.line_transformer import LineParams, LineTransformer
from embedm_plugins.plugin_resources import render_error_note, str_resources
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
            )
        )

        source_path = plan_node.directive.source
        region = plan_node.directive.options.get("region")
        line_range = plan_node.directive.options.get("lines")
        symbol = plan_node.directive.options.get("symbol")

        content = _apply_extraction(compiled, source_path, region, line_range, symbol)
        if isinstance(content, Status):
            return render_error_note([content.description])

        is_markdown = Path(source_path).suffix.lower() in _MARKDOWN_EXTENSIONS
        if not is_markdown:
            ext = Path(source_path).suffix.lstrip(".") or "text"
            return f"```{ext}\n{content.rstrip()}\n```"

        return content


def _apply_region(compiled: str, region: str, source_path: str) -> str | Status:
    result = RegionTransformer().execute(RegionParams(content=compiled, region_name=region))
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


def _apply_extraction(
    compiled: str,
    source_path: str,
    region: str | None,
    line_range: str | None,
    symbol: str | None,
) -> str | Status:
    """Apply the appropriate extraction step and return the result or an error Status."""
    if region:
        return _apply_region(compiled, region, source_path)
    if line_range:
        return _apply_lines(compiled, line_range)
    if symbol:
        return _apply_symbol(compiled, symbol, source_path)
    return compiled
