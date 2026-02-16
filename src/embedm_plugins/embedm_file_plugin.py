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
from embedm_plugins.embedm_file_transformer import EmbedmFileParams, EmbedmFileTransformer

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


class EmbedmFilePlugin(PluginBase):
    name = "embedm file plugin"
    api_version = 1
    directive_type = "embedm_file"

    def validate_directive(self, directive: Directive, _configuration: PluginConfiguration) -> list[Status]:
        if not directive.source:
            return [Status(StatusLevel.ERROR, "embedm_file directive requires a source")]
        return []

    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        file_cache: FileCache | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> str:
        if plan_node.document is None or file_cache is None or plugin_registry is None:
            return ""

        transformer = EmbedmFileTransformer()
        return transformer.execute(
            EmbedmFileParams(
                plan_node=plan_node,
                parent_document=parent_document,
                file_cache=file_cache,
                plugin_registry=plugin_registry,
            )
        )
