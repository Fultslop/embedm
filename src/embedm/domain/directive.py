from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, overload

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

    @overload
    def get_option(self, name: str) -> str | None:
        return self.options.get(name)

    @overload
    def get_option(self, name: str, cast: Callable[[str], T]) -> T | None: ...

    def get_option(self, name: str, cast: Callable[[str], Any] | None = None) -> Any | Status:
        value = self.options.get(name)

        if value is None:
            return None

        if cast:
            # If we expect a bool, but got something that isn't a bool (like "foo" or 42)
            # Because... truthiness...
            if cast is bool and not isinstance(value, bool):  # type: ignore[unreachable]
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

        return value
