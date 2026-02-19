from importlib.metadata import EntryPoint
from unittest.mock import MagicMock, patch

from embedm.domain.status_level import StatusLevel
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
        assert registry.get_plugin("foo") is None


def test_reject_plugin():
    plugin_name = "hello_world"
    mock_plugin_instance = MagicMock(spec=PluginBase)
    mock_plugin_instance.name = plugin_name
    mock_plugin_instance.directive_type = "mock_type"
    mock_plugin_instance.transform.return_value = "transformed_content"

    mock_class = MagicMock(return_value=mock_plugin_instance)

    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "hello_world"
    mock_ep.value = "embedm_plugins.hello_world_plugin:HelloWorldPlugin"
    mock_ep.load.return_value = mock_class

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]

        registry = PluginRegistry()

        # only allow a different module — hello_world_plugin should be skipped
        registry.load_plugins(enabled_modules={"embedm_plugins.other_plugin"}, verbose=True)

        assert registry.count == 0
        assert registry.get_plugin(plugin_name) is None


def test_load_plugins_returns_error_on_failure():
    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "broken_plugin"
    mock_ep.load.side_effect = ImportError("missing dependency")

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]

        registry = PluginRegistry()
        errors = registry.load_plugins()

        assert registry.count == 0
        assert len(errors) == 1
        assert errors[0].level == StatusLevel.ERROR
        assert "broken_plugin" in errors[0].description
        assert "missing dependency" in errors[0].description


def test_load_plugins_skips_failed_and_loads_rest():
    broken_ep = MagicMock(spec=EntryPoint)
    broken_ep.name = "broken_plugin"
    broken_ep.load.side_effect = RuntimeError("bad plugin")

    working_plugin = MagicMock(spec=PluginBase)
    working_plugin.name = "working_plugin"
    working_plugin.directive_type = "working"
    working_class = MagicMock(return_value=working_plugin)
    working_ep = MagicMock(spec=EntryPoint)
    working_ep.name = "working_plugin"
    working_ep.load.return_value = working_class

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        mock_entry_points.return_value = [broken_ep, working_ep]

        registry = PluginRegistry()
        errors = registry.load_plugins()

        assert registry.count == 1
        assert registry.get_plugin("working_plugin") is not None
        assert len(errors) == 1
        assert errors[0].level == StatusLevel.ERROR


# --- find_plugin_by_directive_type ---


def test_find_plugin_by_directive_type_returns_matching_plugin():
    registry = PluginRegistry()
    mock_plugin = MagicMock(spec=PluginBase)
    mock_plugin.name = "hello_world"
    mock_plugin.directive_type = "hello_world"
    registry.lookup["hello_world"] = mock_plugin

    result = registry.find_plugin_by_directive_type("hello_world")

    assert result is mock_plugin


def test_find_plugin_by_directive_type_returns_none_when_not_found():
    registry = PluginRegistry()
    mock_plugin = MagicMock(spec=PluginBase)
    mock_plugin.name = "hello_world"
    mock_plugin.directive_type = "hello_world"
    registry.lookup["hello_world"] = mock_plugin

    result = registry.find_plugin_by_directive_type("unknown_type")

    assert result is None


def test_find_plugin_by_directive_type_empty_registry():
    registry = PluginRegistry()

    result = registry.find_plugin_by_directive_type("hello_world")

    assert result is None
