from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, Generic, TypeVar

from embedm.domain.status_level import Status

TParams = TypeVar("TParams")
TArtifact = TypeVar("TArtifact")


# default implementation for a no params plugin
@dataclass
class NoParams:
    pass


@dataclass
class ValidationResult(Generic[TArtifact]):
    """Typed result of a validation step. Either errors are present or an artifact is returned."""

    artifact: TArtifact | None
    errors: list[Status] = field(default_factory=list)


class ValidationBase(ABC, Generic[TParams, TArtifact]):
    """Base class for plugin input validators."""

    params_type: ClassVar[type]

    @abstractmethod
    def validate(self, params: TParams) -> ValidationResult[TArtifact]:
        pass
