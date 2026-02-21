from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from embedm.domain.domain_resources import str_resources
from embedm.domain.status_level import Status, StatusLevel

T = TypeVar("T")

_BOOL_STRINGS: dict[str, bool] = {"True": True, "False": False}


@dataclass
class Directive:
    type: str
    # source file, may be None if a directive does not use an input file
    # eg ToC
    source: str = ""
    options: dict[str, str] = field(default_factory=dict)
    # directory of the file that contains this directive (for relative link computation)
    base_dir: str = ""

    def validate_option(self, name: str, cast: Callable[[str], Any]) -> Status | None:
        """Check if the option can be cast to the requested type. Returns Status on failure, None if valid or absent."""
        value = self.options.get(name)
        return None if value is None else _validate_cast(name, value, cast)

    def get_option(self, name: str, cast: Callable[[str], T], default_value: T) -> T:
        """Return the option cast to T. Returns default_value if absent or invalid."""
        value = self.options.get(name)
        return default_value if value is None else _get_cast(name, value, cast, default_value)


def _validate_cast(name: str, value: str, cast: Callable[[str], Any]) -> Status | None:
    result = _parse_value(name, value, cast)
    return result if isinstance(result, Status) else None


def _get_cast(name: str, value: str, cast: Callable[[str], T], default_value: T) -> T:
    result = _parse_value(name, value, cast)
    return default_value if isinstance(result, Status) else result


def _parse_value(name: str, value: str, cast: Callable[[str], Any]) -> Any:
    return _cast_bool(name, value) if cast is bool else _try_cast(name, value, cast)


def _cast_bool(name: str, value: str) -> bool | Status:
    result = _BOOL_STRINGS.get(value)
    if result is None:
        return Status(
            StatusLevel.ERROR,
            str_resources.cannot_cast_directive_option.format(name=name, cast_name="bool", value=value),
        )
    return result


def _try_cast(name: str, value: str, cast: Callable[[str], T]) -> T | Status:
    try:
        return cast(value)
    except (ValueError, TypeError):
        cast_name = getattr(cast, "__name__", str(cast))
        return Status(
            StatusLevel.ERROR,
            str_resources.cannot_cast_directive_option.format(name=name, cast_name=cast_name, value=value),
        )
