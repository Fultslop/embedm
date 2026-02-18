from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from embedm.domain.domain_resources import str_resources
from embedm.domain.status_level import Status, StatusLevel

T = TypeVar("T")


@dataclass
class Directive:
    type: str
    # source file, may be None if a directive does not use an input file
    # eg ToC
    source: str = ""
    options: dict[str, str] = field(default_factory=dict)

    def get_option(self, name: str, cast: Callable[[str], T], default_value: T | None = None) -> T | Status | None:
        value = self.options.get(name)

        if value is None:
            return default_value

        # If we expect a bool, but got something that isn't a bool (like "foo" or 42)
        # Because... truthiness...
        if _is_boolean(cast, value):
            return Status(
                StatusLevel.ERROR,
                str_resources.cannot_cast_directive_option.format(name=name, cast_name="bool", value=value),
            )

        try:
            # Use .__name__ to get "int", "float", etc. for the error message
            cast_name = getattr(cast, "__name__", str(cast))
            return cast(value)
        except (ValueError, TypeError):
            # input error so return a status
            return Status(
                StatusLevel.ERROR,
                str_resources.cannot_cast_directive_option.format(name=name, cast_name=cast_name, value=value),
            )


def _is_boolean(f: Callable[[str], T], value: Any) -> bool:
    return f is bool and not isinstance(value, bool)
