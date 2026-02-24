from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, ClassVar

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_context import PluginContext
from embedm.plugins.validation_base import ValidationResult


class PluginBase(ABC):
    name: ClassVar[str]
    api_version: ClassVar[int]
    directive_type: ClassVar[str]

    def get_plugin_config_schema(self) -> dict[str, type] | None:
        """Return accepted config keys and their expected types, or None if plugin takes no config."""
        return None

    def validate_plugin_config(self, _settings: dict[str, Any]) -> list[Status]:
        """Validate semantic constraints on plugin-level config. Override as needed."""
        return []

    def validate_directive(
        self, _directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        """Validate the directive before planning. Override to add directive-level checks.

        The default implementation accepts any directive without error.
        """
        return []

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
        context: PluginContext | None = None,
    ) -> str:
        pass
