from embedm.application.configuration import Configuration
from embedm.domain.status_level import StatusLevel
from embedm.application.plugin_diagnostics import PluginDiagnostics
from embedm.plugins.plugin_registry import PluginRegistry


def _registry_with_discovered(modules: list[str]) -> PluginRegistry:
    registry = PluginRegistry()
    registry.discovered = [(m.split(".")[-1], m) for m in modules]
    return registry


def test_unresolved_module_returns_warning():
    config = Configuration(plugin_sequence=["my_pkg.my_plugin"])
    registry = _registry_with_discovered([])

    statuses = PluginDiagnostics().check(registry, config)

    assert len(statuses) == 1
    assert statuses[0].level == StatusLevel.WARNING
    assert "my_pkg.my_plugin" in statuses[0].description


def test_resolved_module_returns_empty():
    config = Configuration(plugin_sequence=["my_pkg.my_plugin"])
    registry = _registry_with_discovered(["my_pkg.my_plugin"])

    statuses = PluginDiagnostics().check(registry, config)

    assert statuses == []


def test_multiple_unresolved_returns_multiple_warnings():
    config = Configuration(plugin_sequence=["pkg.a", "pkg.b", "pkg.c"])
    registry = _registry_with_discovered(["pkg.b"])

    statuses = PluginDiagnostics().check(registry, config)

    assert len(statuses) == 2
    descriptions = [s.description for s in statuses]
    assert any("pkg.a" in d for d in descriptions)
    assert any("pkg.c" in d for d in descriptions)
    assert all(s.level == StatusLevel.WARNING for s in statuses)


def test_empty_plugin_sequence_returns_empty():
    config = Configuration(plugin_sequence=[])
    registry = _registry_with_discovered([])

    statuses = PluginDiagnostics().check(registry, config)

    assert statuses == []


def test_discovered_superset_of_sequence_returns_empty():
    config = Configuration(plugin_sequence=["pkg.a"])
    registry = _registry_with_discovered(["pkg.a", "pkg.b", "pkg.c"])

    statuses = PluginDiagnostics().check(registry, config)

    assert statuses == []
