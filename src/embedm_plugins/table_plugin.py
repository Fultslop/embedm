from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm_plugins.plugin_resources import str_resources
from embedm_plugins.table_transformer import (
    DATE_FORMAT_KEY,
    DEFAULT_LIMIT,
    DEFAULT_MAX_CELL_LENGTH,
    DEFAULT_NULL_STRING,
    DEFAULT_OFFSET,
    FILTER_KEY,
    LIMIT_KEY,
    MAX_CELL_LENGTH_KEY,
    NULL_STRING_KEY,
    OFFSET_KEY,
    ORDER_BY_KEY,
    SELECT_KEY,
    SUPPORTED_EXTENSIONS,
    TABLE_OPTION_KEY_TYPES,
    TableParams,
    TableTransformer,
)

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


def _validate_filter(filter_str: str) -> list[Status]:
    try:
        parsed = json.loads(filter_str)
        if not isinstance(parsed, dict):
            return [Status(StatusLevel.ERROR, "'filter' must be a mapping of column names to conditions")]
        return []
    except json.JSONDecodeError:
        return [Status(StatusLevel.ERROR, "'filter' must be a valid YAML mapping")]


def _validate_options(directive: Directive) -> list[Status]:
    errors: list[Status] = []
    for key, cast_type in TABLE_OPTION_KEY_TYPES.items():
        if (status := directive.validate_option(key, cast=cast_type)) is not None:
            errors.append(status)
    return errors


def _build_params(directive: Directive, content: str, ext: str) -> TableParams:
    filter_str = directive.options.get(FILTER_KEY)
    filter_map: dict[str, str] = json.loads(filter_str) if filter_str else {}
    return TableParams(
        content=content,
        file_ext=ext,
        select=directive.options.get(SELECT_KEY, ""),
        order_by=directive.options.get(ORDER_BY_KEY, ""),
        limit=directive.get_option(LIMIT_KEY, cast=int, default_value=DEFAULT_LIMIT),
        offset=directive.get_option(OFFSET_KEY, cast=int, default_value=DEFAULT_OFFSET),
        filter_map=filter_map,
        date_format=directive.options.get(DATE_FORMAT_KEY, ""),
        null_string=directive.options.get(NULL_STRING_KEY, DEFAULT_NULL_STRING),
        max_cell_length=directive.get_option(MAX_CELL_LENGTH_KEY, cast=int, default_value=DEFAULT_MAX_CELL_LENGTH),
    )


class TablePlugin(PluginBase):
    """Plugin that renders CSV, TSV, or JSON files as markdown tables."""

    name = "table plugin"
    api_version = 1
    directive_type = "table"

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        assert directive is not None, "directive is required — orchestration must provide it"

        if not directive.source:
            return [Status(StatusLevel.ERROR, "'table' directive requires a source")]

        ext = Path(directive.source).suffix.lower().lstrip(".")
        errors: list[Status] = []
        if ext not in SUPPORTED_EXTENSIONS:
            errors.append(Status(StatusLevel.ERROR, str_resources.err_table_unsupported_format.format(ext=ext)))

        errors.extend(_validate_options(directive))

        filter_str = directive.options.get(FILTER_KEY)
        if filter_str is not None:
            errors.extend(_validate_filter(filter_str))

        return errors

    def transform(
        self,
        plan_node: PlanNode,
        _parent_document: Sequence[Fragment],
        file_cache: FileCache | None = None,
        _plugin_registry: PluginRegistry | None = None,
    ) -> str:
        assert file_cache is not None, "file_cache is required — orchestration must provide it"

        if plan_node.document is None:
            return ""

        content, errors = file_cache.get_file(plan_node.directive.source)
        assert not errors and content is not None, "data file should be cached after planning"

        ext = Path(plan_node.directive.source).suffix.lower().lstrip(".")
        return TableTransformer().execute(_build_params(plan_node.directive, content, ext))
