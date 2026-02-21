from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.validation_base import ValidationResult

from .plugin_configuration import PluginConfiguration

if TYPE_CHECKING:
    from .plugin_registry import PluginRegistry


class PluginBase(ABC):
    name: ClassVar[str]
    api_version: ClassVar[int]
    directive_type: ClassVar[str]

    @abstractmethod
    def validate_directive(
        self, directive: Directive, configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        pass

    def validate_input(
        self,
        _directive: Directive,
        _content: str,
        _plugin_config: PluginConfiguration | None = None,
    ) -> ValidationResult[Any]:
        """Validate file content before transformation. Override in plugins that require it.

        Returns a ValidationResult with an artifact on success, or errors on failure.
        The artifact is stored on the PlanNode and made available to transform().
        """
        return ValidationResult(artifact=None)

    @abstractmethod
    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        file_cache: FileCache | None = None,
        plugin_registry: PluginRegistry | None = None,
        plugin_config: PluginConfiguration | None = None,
    ) -> str:
        pass
