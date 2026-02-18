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
from embedm_plugins.toc_transformer import (
    ADD_SLUGS_KEY,
    MAX_DEPTH_KEY,
    START_FRAGMENT_KEY,
    TOC_OPTION_KEY_TYPES,
    ToCParams,
    ToCTransformer,
)

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
        if not parent_document:
            return ""

        transformer = ToCTransformer()

        # get the start fragment if defined in the options (unlikely but..)
        start_fragment = _get_start_fragment(plan_node, parent_document)

        max_depth = plan_node.directive.get_option(MAX_DEPTH_KEY, cast=int, default_value=5)
        add_slugs = plan_node.directive.get_option(ADD_SLUGS_KEY, cast=bool, default_value=False)

        # satisfy MyPy
        assert isinstance(max_depth, int), f"Expected int, got {type(max_depth)}"
        assert isinstance(add_slugs, bool), f"Expected bool, got {type(add_slugs)}"

        return transformer.execute(ToCParams(parent_document, start_fragment, max_depth, add_slugs))


def _get_start_fragment(plan_node: PlanNode, parent_document: Sequence[Fragment]) -> int:
    # get the start fragment if defined in the options (unlikely but..)
    start_fragment = plan_node.directive.get_option(START_FRAGMENT_KEY, cast=int, default_value=-1)

    if start_fragment == -1:
        # if start_fragment is not defined, get it starting
        # from the ToC directive in the parent_doc, 0 as fallback
        start_fragment = next((i for i, x in enumerate(parent_document) if x is plan_node.directive), 0)

    # this should have been verified via validate, if not crash and burn
    assert isinstance(start_fragment, int), f"Expected int, got {type(start_fragment)}"

    return start_fragment
