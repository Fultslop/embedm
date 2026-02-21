from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from embedm.domain.status_level import Status

TParams = TypeVar("TParams")


# default implementation for a no params plugin
@dataclass
class NoParams:
    pass


class ValidationBase(ABC, Generic[TParams]):
    params_type: ClassVar[type[TParams]]

    @abstractmethod
    def validate(self, params: TParams) -> Any | list[Status]:
        pass
