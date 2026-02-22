from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass
from typing import Any

from embedm.domain.status_level import Status, StatusLevel
from embedm.plugins.validation_base import ValidationBase, ValidationResult
from embedm_plugins.table_resources import str_resources

Row = dict[str, str]

_SELECT_ALIAS_PATTERN = re.compile(r"^\s*(\w+)(?:\s+as\s+(\w+))?\s*$", re.IGNORECASE)
_ORDER_BY_PATTERN = re.compile(r"^\s*(\w+)(?:\s+(asc|desc))?\s*$", re.IGNORECASE)


@dataclass
class CsvTsvValidationParams:
    """Parameters for CSV/TSV table content validation."""

    content: str
    delimiter: str
    select: str
    order_by: str


@dataclass
class JsonValidationParams:
    """Parameters for JSON table content validation."""

    content: str
    select: str
    order_by: str


def _parse_delimited(content: str, delimiter: str) -> list[Row]:
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    return [{str(k): (str(v) if v is not None else "") for k, v in row.items()} for row in reader]


def _parse_json_rows(content: str) -> tuple[list[Row], list[Status]]:
    try:
        data: Any = json.loads(content)
    except json.JSONDecodeError as exc:
        return [], [Status(StatusLevel.ERROR, str_resources.err_table_invalid_json.format(exc=exc))]

    if not isinstance(data, list):
        msg = str_resources.err_table_json_not_array.format(type_name=type(data).__name__)
        return [], [Status(StatusLevel.ERROR, msg)]

    if not all(isinstance(row, dict) for row in data):
        return [], [Status(StatusLevel.ERROR, str_resources.err_table_json_not_objects)]

    return [{str(k): _json_value_to_str(v) for k, v in row.items()} for row in data], []


def _json_value_to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _validate_select(rows: list[Row], select_str: str) -> list[Status]:
    """Validate select expression syntax and column existence against parsed rows."""
    if not select_str or not rows:
        return []

    errors: list[Status] = []
    available = set(rows[0].keys())

    for part in select_str.split(","):
        match = _SELECT_ALIAS_PATTERN.match(part)
        if not match:
            errors.append(Status(StatusLevel.ERROR, str_resources.err_table_invalid_select.format(expr=part.strip())))
            continue
        src_col = match.group(1)
        if src_col not in available:
            msg = str_resources.err_table_column_not_found.format(col=src_col, available=", ".join(sorted(available)))
            errors.append(Status(StatusLevel.ERROR, msg))

    return errors


def _validate_order_by(order_by_str: str) -> list[Status]:
    """Validate order_by expression syntax."""
    if not order_by_str:
        return []

    errors: list[Status] = []
    for part in order_by_str.split(","):
        if not _ORDER_BY_PATTERN.match(part):
            errors.append(Status(StatusLevel.ERROR, str_resources.err_table_invalid_order_by.format(expr=part.strip())))

    return errors


class CsvTsvTableValidation(ValidationBase[CsvTsvValidationParams, list[Row]]):
    """Validates CSV and TSV table content, returning parsed rows as artifact."""

    params_type = CsvTsvValidationParams

    def validate(self, params: CsvTsvValidationParams) -> ValidationResult[list[Row]]:
        """Parse and validate CSV/TSV content. Returns rows as artifact on success."""
        rows = _parse_delimited(params.content, params.delimiter)

        if not rows:
            empty_error = Status(StatusLevel.ERROR, str_resources.err_table_empty_content)
            return ValidationResult(artifact=None, errors=[empty_error])

        errors = _validate_select(rows, params.select) + _validate_order_by(params.order_by)
        if errors:
            return ValidationResult(artifact=None, errors=errors)

        return ValidationResult(artifact=rows)


class JsonTableValidation(ValidationBase[JsonValidationParams, list[Row]]):
    """Validates JSON table content, returning parsed rows as artifact."""

    params_type = JsonValidationParams

    def validate(self, params: JsonValidationParams) -> ValidationResult[list[Row]]:
        """Parse and validate JSON content. Returns rows as artifact on success."""
        rows, errors = _parse_json_rows(params.content)
        if errors:
            return ValidationResult(artifact=None, errors=errors)

        if not rows:
            empty_error = Status(StatusLevel.ERROR, str_resources.err_table_empty_content)
            return ValidationResult(artifact=None, errors=[empty_error])

        errors = _validate_select(rows, params.select) + _validate_order_by(params.order_by)
        if errors:
            return ValidationResult(artifact=None, errors=errors)

        return ValidationResult(artifact=rows)
