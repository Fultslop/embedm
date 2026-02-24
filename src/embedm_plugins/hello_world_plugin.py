from collections.abc import Sequence

from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.plugins.api import PluginBase
from embedm.plugins.plugin_context import PluginContext
from embedm.plugins.transformer_base import NoParams
from embedm_plugins.hello_world_transformer import HelloWorldTransformer


class HelloWorldPlugin(PluginBase):
    name = "hello world plugin"
    api_version = 1
    directive_type = "hello_world"

    def transform(
        self, _plan_node: PlanNode, _parent_document: Sequence[Fragment], _context: PluginContext | None = None
    ) -> str:
        return HelloWorldTransformer().execute(NoParams())
