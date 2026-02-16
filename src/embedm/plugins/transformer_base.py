from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Generic, TypeVar

TParams = TypeVar("TParams")


# default implementation for a no params plugin
@dataclass
class NoParams:
    pass


class TransformerBase(ABC, Generic[TParams]):
    params_type: ClassVar[type[TParams]]

    @abstractmethod
    def execute(self, params: TParams) -> str:
        pass
