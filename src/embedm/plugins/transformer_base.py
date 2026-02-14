from abc import ABC, abstractmethod

from embedm.domain.directive import Directive
from embedm.io.file_cache import FileCache


class TransformerBase(ABC):

    @abstractmethod
    def transform(self, directive: Directive, file_cache : FileCache) -> str:
        pass
