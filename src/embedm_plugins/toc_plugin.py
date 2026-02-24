from __future__ import annotations

from collections.abc import Sequence

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status
from embedm.plugins.directive_options import get_option, validate_option
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_context import PluginContext
from embedm_plugins.toc_transformer import (
    ADD_SLUGS_KEY,
    MAX_DEPTH_KEY,
    START_FRAGMENT_KEY,
    TOC_OPTION_KEY_TYPES,
    ToCParams,
    ToCTransformer,
)


class ToCPlugin(PluginBase):
    name = "toc plugin"
    api_version = 1
    directive_type = "toc"  # TODO: allow for table_of_contents

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        assert directive is not None, "directive is required — orchestration must provide it"

        return [
            status
            for key, cast_type in TOC_OPTION_KEY_TYPES.items()
            if (status := validate_option(directive, key, cast=cast_type)) is not None
        ]

    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        _context: PluginContext | None = None,
    ) -> str:
        if not parent_document:
            return ""

        transformer = ToCTransformer()

        start_fragment = _get_start_fragment(plan_node, parent_document)
        max_depth = get_option(plan_node.directive, MAX_DEPTH_KEY, cast=int, default_value=5)
        add_slugs = get_option(plan_node.directive, ADD_SLUGS_KEY, cast=bool, default_value=False)

        return transformer.execute(ToCParams(parent_document, start_fragment, max_depth, add_slugs))


def _get_start_fragment(plan_node: PlanNode, parent_document: Sequence[Fragment]) -> int:
    start_fragment = get_option(plan_node.directive, START_FRAGMENT_KEY, cast=int, default_value=-1)

    if start_fragment == -1:
        start_fragment = next((i for i, x in enumerate(parent_document) if x is plan_node.directive), 0)

    return start_fragment
