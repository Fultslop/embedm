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
from embedm_plugins.file_transformer import FileParams, FileTransformer

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


class FilePlugin(PluginBase):
    name = "file plugin"
    api_version = 1
    directive_type = "file"

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        if not directive.source:
            return [Status(StatusLevel.ERROR, "'file' directive requires a source")]
        return []

    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        file_cache: FileCache | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> str:
        assert file_cache is not None, "file_cache is required — orchestration must provide it"
        assert plugin_registry is not None, "plugin_registry is required — orchestration must provide it"

        if plan_node.document is None:
            return ""

        transformer = FileTransformer()
        return transformer.execute(
            FileParams(
                plan_node=plan_node,
                parent_document=parent_document,
                file_cache=file_cache,
                plugin_registry=plugin_registry,
            )
        )
