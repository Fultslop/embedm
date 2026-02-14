import unittest

from embedm.plugins.transformer_base import NoParams
from embedm_plugins.hello_world_transformer import HelloWorldTransformer

class HelloWorldPluginTest(unittest.TestCase):

    def test_transformer(self):
        transformer = HelloWorldTransformer()
        self.assertEqual(transformer.execute(NoParams()), 'hello embedded world!')