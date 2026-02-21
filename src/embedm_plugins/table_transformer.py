from __future__ import annotations

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
    """Parameters for the table transformer. Rows are pre-parsed by the validation step."""

    rows: list[Row]
    select: str = ""
    order_by: str = ""
    limit: int = DEFAULT_LIMIT
    offset: int = DEFAULT_OFFSET
    filter_map: dict[str, str] = field(default_factory=dict)
    date_format: str = ""
    null_string: str = DEFAULT_NULL_STRING
    max_cell_length: int = DEFAULT_MAX_CELL_LENGTH


class TableTransformer(TransformerBase[TableParams]):
    """Transforms pre-parsed tabular rows into a markdown table."""

    params_type = TableParams

    def execute(self, params: TableParams) -> str:
        if not params.rows:
            return str(str_resources.note_no_results) + "\n"

        rows, headers = _apply_pipeline(params.rows, params)

        if not rows:
            return str(str_resources.note_no_results) + "\n"

        return _render_table(rows, headers, params.date_format, params.null_string, params.max_cell_length)


def _apply_pipeline(rows: list[Row], params: TableParams) -> tuple[list[Row], list[str]]:
    """Run filter → select → order_by → slice. Returns (rows, headers)."""
    if params.filter_map:
        rows = _apply_filter(rows, params.filter_map)

    if params.select:
        rows, headers = _apply_select(rows, params.select)
    else:
        headers = list(rows[0].keys()) if rows else []

    if params.order_by:
        rows = _apply_order_by(rows, params.order_by)

    rows = rows[params.offset :]
    if params.limit >= 0:
        rows = rows[: params.limit]

    return rows, headers


def _apply_filter(rows: list[Row], filter_map: dict[str, str]) -> list[Row]:
    """Filter rows, keeping only those matching all conditions. All keys are ANDed."""
    filtered: list[Row] = []
    for row in rows:
        include = True
        for col, condition in filter_map.items():
            if not _evaluate_condition(row.get(col, ""), condition):
                include = False
                break
        if include:
            filtered.append(row)
    return filtered


def _evaluate_condition(row_value: str, condition: str) -> bool:
    match = _FILTER_OP_PATTERN.match(condition)
    if match:
        operator_str, target = match.group(1), match.group(2).strip()
    else:
        operator_str, target = "=", condition

    compare_fn = _OPERATORS[operator_str]

    try:
        return compare_fn(float(row_value), float(target))
    except ValueError:
        pass

    return compare_fn(row_value, target)


def _apply_select(rows: list[Row], select_str: str) -> tuple[list[Row], list[str]]:
    """Project and rename columns per select_str (e.g. 'col_a, col_b as b').

    Precondition: select_str syntax and column existence validated by validate_input.
    """
    column_map: list[tuple[str, str]] = []
    for part in select_str.split(","):
        match = _SELECT_ALIAS_PATTERN.match(part)
        assert match is not None, f"invalid select expression '{part.strip()}' — must be caught by validate_input"
        src_col = match.group(1)
        alias = match.group(2) or src_col
        column_map.append((src_col, alias))

    if rows:
        available = set(rows[0].keys())
        for src_col, _ in column_map:
            assert src_col in available, f"column '{src_col}' not found — must be caught by validate_input"

    new_rows = [{alias: row.get(src_col, "") for src_col, alias in column_map} for row in rows]
    headers = [alias for _, alias in column_map]
    return new_rows, headers


def _apply_order_by(rows: list[Row], order_by_str: str) -> list[Row]:
    """Sort rows per order_by_str (e.g. 'col_a desc, col_b'). Later specs = higher priority.

    Precondition: order_by_str syntax validated by validate_input.
    """
    specs: list[tuple[str, bool]] = []
    for part in order_by_str.split(","):
        match = _ORDER_BY_PATTERN.match(part)
        assert match is not None, f"invalid order_by expression '{part.strip()}' — must be caught by validate_input"
        col = match.group(1)
        direction = (match.group(2) or "asc").lower()
        specs.append((col, direction == "desc"))

    result = list(rows)
    for col, reverse in reversed(specs):
        result = sorted(result, key=lambda r: _sort_key(r.get(col, "")), reverse=reverse)
    return result


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
