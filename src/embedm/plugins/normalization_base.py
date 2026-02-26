from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, Generic, TypeVar

from embedm.domain.status_level import Status

TParams = TypeVar("TParams")
TNormalizedData = TypeVar("TNormalizedData")


# default implementation for a no params plugin
@dataclass
class NoParams:
    pass


@dataclass
class NormalizationResult(Generic[TNormalizedData]):
    """Typed result of a validation step. Either errors are present or an normalized_data is returned."""

    normalized_data: TNormalizedData | None
    errors: list[Status] = field(default_factory=list)


class NormalizationBase(ABC, Generic[TParams, TNormalizedData]):
    """Base class for plugin input validators."""

    params_type: ClassVar[type]

    @abstractmethod
    def validate(self, params: TParams) -> NormalizationResult[TNormalizedData]:
        pass
