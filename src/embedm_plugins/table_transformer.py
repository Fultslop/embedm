from __future__ import annotations

import csv
import io
import json
import operator as op
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from embedm.plugins.transformer_base import TransformerBase
from embedm_plugins.plugin_resources import str_resources

SELECT_KEY = "select"
ORDER_BY_KEY = "order_by"
LIMIT_KEY = "limit"
OFFSET_KEY = "offset"
DATE_FORMAT_KEY = "date_format"
NULL_STRING_KEY = "null_string"
MAX_CELL_LENGTH_KEY = "max_cell_length"
FILTER_KEY = "filter"

TABLE_OPTION_KEY_TYPES = {
    LIMIT_KEY: int,
    OFFSET_KEY: int,
    MAX_CELL_LENGTH_KEY: int,
    # Review: where are the rest of the keys, filter, null_str and so on ?
}

# Review: TODO We'll need to implement plugin configurations, discuss
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({"csv", "tsv", "json"})

DEFAULT_NULL_STRING = ""
DEFAULT_MAX_CELL_LENGTH = 0  # 0 = no truncation
DEFAULT_LIMIT = -1  # -1 = no limit
DEFAULT_OFFSET = 0

_SELECT_ALIAS_PATTERN = re.compile(r"^\s*(\w+)(?:\s+as\s+(\w+))?\s*$", re.IGNORECASE)
_ORDER_BY_PATTERN = re.compile(r"^\s*(\w+)(?:\s+(asc|desc))?\s*$", re.IGNORECASE)
_FILTER_OP_PATTERN = re.compile(r"^(!=|<=|>=|<|>|=)\s*(.+)$")

_OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "=": op.eq,
    "!=": op.ne,
    "<": op.lt,
    "<=": op.le,
    ">": op.gt,
    ">=": op.ge,
}

Row = dict[str, str]


@dataclass
class TableParams:
    """Parameters for the table transformer."""

    content: str
    file_ext: str
    select: str = ""
    order_by: str = ""
    limit: int = DEFAULT_LIMIT
    offset: int = DEFAULT_OFFSET
    filter_map: dict[str, str] = field(default_factory=dict)
    date_format: str = ""
    null_string: str = DEFAULT_NULL_STRING
    max_cell_length: int = DEFAULT_MAX_CELL_LENGTH


class TableTransformer(TransformerBase[TableParams]):
    """Transforms tabular data (CSV/TSV/JSON) into a markdown table."""

    params_type = TableParams

    def execute(self, params: TableParams) -> str:
        # Review: Plugin should validate, any errors at this point are programming
        # errors. The question then is, is this possible for something like this transformer
        # as content errors may be ligitimate user errors. TODO discuss
        rows, error = _parse_content(params.content, params.file_ext)
        if error:
            return error

        if not rows:
            return str(str_resources.note_no_table_content) + "\n"

        rows, headers, error = _apply_pipeline(rows, params)
        if error:
            return error

        if not rows:
            return str(str_resources.note_no_table_content) + "\n"

        return _render_table(rows, headers, params.date_format, params.null_string, params.max_cell_length)


def _parse_content(content: str, ext: str) -> tuple[list[Row], str | None]:
    """Parse file content into rows. Returns (rows, error_string)."""

    # Review: avoid hardcoded strings
    if ext == "csv":
        return _parse_delimited(content, ","), None
    if ext == "tsv":
        return _parse_delimited(content, "\t"), None
    if ext == "json":
        return _parse_json(content)
    return [], _render_error(str_resources.err_table_unsupported_format.format(ext=ext))


def _parse_delimited(content: str, delimiter: str) -> list[Row]:
    # Review: Could have used a comments to capture intention.
    # Guess it's hard to determine when it's needed and not. TODO Discuss
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    return [{str(k): (str(v) if v is not None else "") for k, v in row.items()} for row in reader]


def _parse_json(content: str) -> tuple[list[Row], str | None]:
    # Review: Again error handling in operational part.
    try:
        data: Any = json.loads(content)
    except json.JSONDecodeError as exc:
        return [], _render_error(str_resources.err_table_invalid_json.format(exc=exc))

    if not isinstance(data, list):
        return [], _render_error(str_resources.err_table_json_not_array.format(type_name=type(data).__name__))

    if not all(isinstance(row, dict) for row in data):
        return [], _render_error(str_resources.err_table_json_not_objects)

    return [{str(k): _json_value_to_str(v) for k, v in row.items()} for row in data], None


def _json_value_to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _apply_pipeline(rows: list[Row], params: TableParams) -> tuple[list[Row], list[str], str | None]:
    """Run filter → select → order_by → slice. Returns (rows, headers, error)."""
    if params.filter_map:
        rows, error = _apply_filter(rows, params.filter_map)
        if error:
            return [], [], error

    if params.select:
        rows, headers, error = _apply_select(rows, params.select)
        if error:
            return [], [], error
    else:
        headers = list(rows[0].keys()) if rows else []

    if params.order_by:
        rows, error = _apply_order_by(rows, params.order_by)
        if error:
            return [], [], error

    rows = rows[params.offset :]
    if params.limit >= 0:
        rows = rows[: params.limit]

    return rows, headers, None


def _apply_filter(rows: list[Row], filter_map: dict[str, str]) -> tuple[list[Row], str | None]:
    """Filter rows, keeping only those matching all conditions. All keys are ANDed."""
    filtered: list[Row] = []
    for row in rows:
        include = True
        for col, condition in filter_map.items():
            matches, error = _evaluate_condition(row.get(col, ""), condition)
            if error:
                return [], error
            if not matches:
                include = False
                break
        if include:
            filtered.append(row)
    return filtered, None


def _evaluate_condition(row_value: str, condition: str) -> tuple[bool, str | None]:
    match = _FILTER_OP_PATTERN.match(condition)
    if match:
        operator_str, target = match.group(1), match.group(2).strip()
    else:
        operator_str, target = "=", condition

    compare_fn = _OPERATORS.get(operator_str)
    if compare_fn is None:
        return False, _render_error(str_resources.err_table_invalid_filter_operator.format(expr=condition))

    try:
        return compare_fn(float(row_value), float(target)), None
    except ValueError:
        pass

    return compare_fn(row_value, target), None


def _apply_select(rows: list[Row], select_str: str) -> tuple[list[Row], list[str], str | None]:
    """Project and rename columns per select_str (e.g. 'col_a, col_b as b')."""
    column_map: list[tuple[str, str]] = []
    for part in select_str.split(","):
        match = _SELECT_ALIAS_PATTERN.match(part)
        if not match:
            return [], [], _render_error(str_resources.err_table_invalid_select.format(expr=part.strip()))
        src_col = match.group(1)
        alias = match.group(2) or src_col
        column_map.append((src_col, alias))

    if rows:
        available = set(rows[0].keys())
        for src_col, _ in column_map:
            if src_col not in available:
                return (
                    [],
                    [],
                    _render_error(
                        str_resources.err_table_column_not_found.format(
                            col=src_col, available=", ".join(sorted(available))
                        )
                    ),
                )

    new_rows = [{alias: row.get(src_col, "") for src_col, alias in column_map} for row in rows]
    headers = [alias for _, alias in column_map]
    return new_rows, headers, None


def _apply_order_by(rows: list[Row], order_by_str: str) -> tuple[list[Row], str | None]:
    """Sort rows per order_by_str (e.g. 'col_a desc, col_b'). Later specs = higher priority."""
    specs: list[tuple[str, bool]] = []
    for part in order_by_str.split(","):
        match = _ORDER_BY_PATTERN.match(part)
        if not match:
            return [], _render_error(str_resources.err_table_invalid_order_by.format(expr=part.strip()))
        col = match.group(1)
        direction = (match.group(2) or "asc").lower()
        specs.append((col, direction == "desc"))

    result = list(rows)
    for col, reverse in reversed(specs):
        result = sorted(result, key=lambda r: _sort_key(r.get(col, "")), reverse=reverse)
    return result, None


def _sort_key(value: str) -> tuple[int, float | str]:
    """Numeric values sort before strings when mixed; within each group uses natural order."""
    try:
        return (0, float(value))
    except ValueError:
        return (1, value)


def _render_table(
    rows: list[Row],
    headers: list[str],
    date_format: str,
    null_string: str,
    max_cell_length: int,
) -> str:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        cells = [_format_cell(row.get(h, ""), date_format, null_string, max_cell_length) for h in headers]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def _format_cell(value: str, date_format: str, null_string: str, max_cell_length: int) -> str:
    if not value:
        return null_string

    if date_format:
        try:
            dt = datetime.fromisoformat(value)
            value = dt.strftime(date_format)
        except ValueError:
            pass

    value = value.replace("|", "\\|").replace("\n", " ").replace("\r", "")

    if max_cell_length > 0 and len(value) > max_cell_length:
        value = value[: max_cell_length - 1] + "\u2026"

    return value


def _render_error(message: str) -> str:
    # Review: strings should be in plugin_resources, probably need per plugin resources
    # TODO discuss
    return f"> [!CAUTION]\n> **embedm:** {message}\n"
