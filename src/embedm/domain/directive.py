from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar

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

    def get_option(self, name: str, cast: Callable[[str], T], default_value: T | None = None) -> T | Status | None:
        """Return the option value cast to the requested type, or a Status on failure."""
        value = self.options.get(name)

        if value is None:
            return default_value

        if cast is bool:
            return _cast_bool(name, value)  # type: ignore[return-value]

        try:
            cast_name = getattr(cast, "__name__", str(cast))
            return cast(value)
        except (ValueError, TypeError):
            return Status(
                StatusLevel.ERROR,
                str_resources.cannot_cast_directive_option.format(name=name, cast_name=cast_name, value=value),
            )


def _cast_bool(name: str, value: str) -> bool | Status:
    result = _BOOL_STRINGS.get(value)
    if result is None:
        return Status(
            StatusLevel.ERROR,
            str_resources.cannot_cast_directive_option.format(name=name, cast_name="bool", value=value),
        )
    return result
