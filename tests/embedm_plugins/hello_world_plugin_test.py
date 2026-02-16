from embedm.domain.directive import Directive
from embedm.domain.plan_node import PlanNode
from embedm.plugins.transformer_base import NoParams
from embedm_plugins.hello_world_plugin import HelloWorldPlugin
from embedm_plugins.hello_world_transformer import HelloWorldTransformer


def test_transformer_execute():
    transformer = HelloWorldTransformer()
    assert transformer.execute(NoParams()) == 'hello embedded world!'


def test_plugin_transform():
    plugin = HelloWorldPlugin()
    node = PlanNode(directive=Directive(type="hello_world"), status=[], document=None, children=None)
    assert plugin.transform(node, []) == 'hello embedded world!'
