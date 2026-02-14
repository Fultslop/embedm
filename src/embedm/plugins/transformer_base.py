from dataclasses import dataclass
from typing import ClassVar, Generic, TypeVar

TParams = TypeVar("TParams")


# default implementation for a no params plugin
@dataclass
class NoParams:
    pass


class TransformerBase(Generic[TParams]):
    params_type: ClassVar[type[TParams]]

    def execute(self, params: TParams) -> str:
        raise NotImplementedError
