from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm_plugins.toc_transformer import ADD_SLUGS_KEY, MAX_DEPTH_KEY, TOC_OPTION_KEY_TYPES, ToCParams, ToCTransformer

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


class ToCPlugin(PluginBase):
    name = "toc plugin"
    api_version = 1
    directive_type = "toc"  # TODO: allow for table_of_contents

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        assert directive is not None, "directive is required — orchestration must provide it"

        status_messages = [
            result
            for key, cast_type in TOC_OPTION_KEY_TYPES.items()
            if isinstance(result := directive.get_option(key, cast=cast_type), Status)
        ]
        return status_messages

    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        _file_cache: FileCache | None = None,
        _plugin_registry: PluginRegistry | None = None,
    ) -> str:
        if parent_document is None or len(parent_document) == 0:
            return ""

        transformer = ToCTransformer()
        return transformer.execute(
            ToCParams(
                max_depth=plan_node.directive.get_option(MAX_DEPTH_KEY, cast=int) or 5,
                add_slugs=plan_node.directive.get_option(ADD_SLUGS_KEY, cast=bool) or False,
                parent_document=parent_document,
            )
        )
