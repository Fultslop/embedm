from abc import ABC, abstractmethod
from typing import ClassVar

from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.status_level import Status
from embedm.io.file_cache import FileCache

from .plugin_configuration import PluginConfiguration


class PluginBase(ABC):
    name: ClassVar[str]
    api_version: ClassVar[int]
    directive_type: ClassVar[str]

    @abstractmethod
    def validate_directive(self, directive: Directive) -> list[Status]:
        pass

    @abstractmethod
    def transform(
        self,
        directive: Directive,
        document: Document | None = None,
        file_cache: FileCache | None = None,
        configuration: PluginConfiguration | None = None,
    ) -> str:
        pass
