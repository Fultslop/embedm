from abc import ABC, abstractmethod

from embedm.domain.directive import Directive
from embedm.io.file_cache import FileCache


class PluginBase(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def validate_directive(self, directive: Directive) -> str:
        pass

    @abstractmethod
    def transform(self, directive: Directive, file_cache : FileCache) -> str:
        pass
