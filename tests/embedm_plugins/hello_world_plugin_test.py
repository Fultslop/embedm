from embedm.domain.directive import Directive
from embedm.plugins.transformer_base import NoParams
from embedm_plugins.hello_world_plugin import HelloWorldPlugin
from embedm_plugins.hello_world_transformer import HelloWorldTransformer

def test_transformer_execute():
    transformer = HelloWorldTransformer()
    assert transformer.execute(NoParams()) == 'hello embedded world!'

def test_plugin_transform():
    plugin = HelloWorldPlugin()
    assert plugin.transform(Directive(type="hello_world")) == 'hello embedded world!'