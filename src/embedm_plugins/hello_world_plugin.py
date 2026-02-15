from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.transformer_base import NoParams
from embedm_plugins.hello_world_transformer import HelloWorldTransformer

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


class HelloWorldPlugin(PluginBase):
    name = "hello world plugin"
    api_version = 1
    directive_type = "hello_world"

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration
    ) -> list[Status]:
        if directive.type != self.directive_type:
            return [
                Status(
                    StatusLevel.FATAL,
                    f"directive type does not match. "
                    f"Expected '{self.directive_type}', provided: '{directive.type}'.",
                )
            ]
        return []

    def transform(
        self,
        _plan_node: PlanNode,
        _parent_document: Sequence[Fragment],
        _file_cache: FileCache | None = None,
        _plugin_registry: PluginRegistry | None = None,
    ) -> str:
        transform = HelloWorldTransformer()
        return transform.execute(NoParams())
