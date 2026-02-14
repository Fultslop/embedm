import unittest

from embedm.domain.directive import Directive
from embedm.plugins.transformer_base import NoParams
from embedm_plugins.hello_world_plugin import HelloWorldPlugin
from embedm_plugins.hello_world_transformer import HelloWorldTransformer

class HelloWorldPluginTest(unittest.TestCase):

    def test_transformer_execute(self):
        transformer = HelloWorldTransformer()
        self.assertEqual(transformer.execute(NoParams()), 'hello embedded world!')

    def test_plugin_transform(self):
        plugin = HelloWorldPlugin()
        self.assertEqual(plugin.transform(Directive(type="hello_world")), 'hello embedded world!')