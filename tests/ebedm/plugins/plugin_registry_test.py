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
    mock_ep.value = "embedm_plugins.hello_world_plugin:HelloWorldPlugin"
    mock_ep.load.return_value = mock_class

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]

        registry = PluginRegistry()

        registry.load_plugins()

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
        registry.load_plugins(enabled_modules={"embedm_plugins.other_plugin"})

        assert registry.count == 0
        assert registry.get_plugin(plugin_name) is None


def test_load_plugins_returns_error_on_failure():
    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "broken_plugin"
    mock_ep.value = "embedm_plugins.broken_plugin:BrokenPlugin"
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
    broken_ep.value = "embedm_plugins.broken_plugin:BrokenPlugin"
    broken_ep.load.side_effect = RuntimeError("bad plugin")

    working_plugin = MagicMock(spec=PluginBase)
    working_plugin.name = "working_plugin"
    working_plugin.directive_type = "working"
    working_class = MagicMock(return_value=working_plugin)
    working_ep = MagicMock(spec=EntryPoint)
    working_ep.name = "working_plugin"
    working_ep.value = "embedm_plugins.working_plugin:WorkingPlugin"
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


# --- missing required attributes ---


class _NoName(PluginBase):
    directive_type = "test_no_name"

    def transform(self, plan_node, parent_document, context=None) -> str:  # type: ignore[override]
        return ""


class _NoDirectiveType(PluginBase):
    name = "test_no_directive_type"

    def transform(self, plan_node, parent_document, context=None) -> str:  # type: ignore[override]
        return ""


class _NoBoth(PluginBase):
    def transform(self, plan_node, parent_document, context=None) -> str:  # type: ignore[override]
        return ""


def _make_ep(ep_name: str, module_value: str, plugin_class: type) -> MagicMock:
    ep = MagicMock(spec=EntryPoint)
    ep.name = ep_name
    ep.value = module_value
    ep.load.return_value = plugin_class
    return ep


def test_duplicate_entry_points_are_loaded_once():
    ep1 = _make_ep("my_plugin", "my_pkg.my_plugin:MyPlugin", MagicMock(spec=PluginBase))
    ep2 = _make_ep("my_plugin", "my_pkg.my_plugin:MyPlugin", MagicMock(spec=PluginBase))

    instance = MagicMock(spec=PluginBase)
    instance.name = "my_plugin"
    instance.directive_type = "my_type"
    ep1.load.return_value = MagicMock(return_value=instance)
    ep2.load.return_value = MagicMock(return_value=instance)

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_eps:
        mock_eps.return_value = [ep1, ep2]
        registry = PluginRegistry()
        errors = registry.load_plugins()

    assert registry.count == 1
    assert len(errors) == 0
    assert len(registry.discovered) == 1


def test_missing_name_returns_fatal_error():
    ep = _make_ep("no_name_plugin", "my_pkg.no_name:_NoName", _NoName)

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_eps:
        mock_eps.return_value = [ep]
        registry = PluginRegistry()
        errors = registry.load_plugins()

    assert registry.count == 0
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.FATAL
    assert "no_name_plugin" in errors[0].description
    assert "'name'" in errors[0].description


def test_missing_directive_type_returns_fatal_error():
    ep = _make_ep("no_dtype_plugin", "my_pkg.no_dtype:_NoDirectiveType", _NoDirectiveType)

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_eps:
        mock_eps.return_value = [ep]
        registry = PluginRegistry()
        errors = registry.load_plugins()

    assert registry.count == 0
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.FATAL
    assert "no_dtype_plugin" in errors[0].description
    assert "'directive_type'" in errors[0].description


def test_missing_both_attributes_lists_all_in_single_error():
    ep = _make_ep("no_both_plugin", "my_pkg.no_both:_NoBoth", _NoBoth)

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_eps:
        mock_eps.return_value = [ep]
        registry = PluginRegistry()
        errors = registry.load_plugins()

    assert registry.count == 0
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.FATAL
    assert "'name'" in errors[0].description
    assert "'directive_type'" in errors[0].description


# --- duplicate directive_type ---


class _Alpha(PluginBase):
    name = "alpha"
    directive_type = "shared_type"

    def transform(self, plan_node, parent_document, context=None) -> str:  # type: ignore[override]
        return ""


class _Beta(PluginBase):
    name = "beta"
    directive_type = "shared_type"

    def transform(self, plan_node, parent_document, context=None) -> str:  # type: ignore[override]
        return ""


def test_duplicate_directive_type_returns_error():
    ep_a = _make_ep("alpha", "my_pkg.alpha:_Alpha", _Alpha)
    ep_b = _make_ep("beta", "my_pkg.beta:_Beta", _Beta)

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_eps:
        mock_eps.return_value = [ep_a, ep_b]
        registry = PluginRegistry()
        errors = registry.load_plugins()

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "shared_type" in errors[0].description


def test_duplicate_directive_type_second_plugin_not_registered():
    ep_a = _make_ep("alpha", "my_pkg.alpha:_Alpha", _Alpha)
    ep_b = _make_ep("beta", "my_pkg.beta:_Beta", _Beta)

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_eps:
        mock_eps.return_value = [ep_a, ep_b]
        registry = PluginRegistry()
        registry.load_plugins()

    assert registry.count == 1
    assert registry.get_plugin("alpha") is not None
    assert registry.get_plugin("beta") is None
