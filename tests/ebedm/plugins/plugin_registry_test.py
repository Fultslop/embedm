from unittest.mock import MagicMock, patch
from importlib.metadata import EntryPoint

from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_registry import PluginRegistry


def test_plugin_discovery():
    plugin_name = "hello_world"
    mock_plugin_instance = MagicMock(spec=PluginBase)
    mock_plugin_instance.name = plugin_name
    mock_plugin_instance.directive_type = "mock_type"
    mock_plugin_instance.transform.return_value = "transformed_content"

    mock_class = MagicMock(return_value=mock_plugin_instance)

    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "hello_world"
    mock_ep.load.return_value = mock_class

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        
        mock_entry_points.return_value = [mock_ep]
        
        registry = PluginRegistry()
       
        registry.load_plugins(verbose=True)
        
        assert registry.count == 1
        assert registry.get_plugin(plugin_name) is not None
        assert registry.get_plugin('foo') is None

def test_reject_plugin():
    plugin_name = "hello_world"
    mock_plugin_instance = MagicMock(spec=PluginBase)
    mock_plugin_instance.name = plugin_name
    mock_plugin_instance.directive_type = "mock_type"
    mock_plugin_instance.transform.return_value = "transformed_content"

    mock_class = MagicMock(return_value=mock_plugin_instance)

    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "hello_world"
    mock_ep.load.return_value = mock_class

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        
        mock_entry_points.return_value = [mock_ep]
        
        registry = PluginRegistry()
       
        # do not allow hello_world
        registry.load_plugins(enabled_plugins=["foo"], verbose=True)
        
        assert registry.count == 0
        assert registry.get_plugin(plugin_name) is None
        assert registry.get_plugin('foo') is None