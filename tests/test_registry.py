"""Tests for plugin registry and dispatcher."""

import pytest
from embedm.registry import PluginRegistry, dispatch_embed, get_default_registry, set_default_registry
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase


class MockPluginA(EmbedPlugin):
    """Mock plugin for testing."""
    @property
    def name(self):
        return "mock_a"

    @property
    def embed_types(self):
        return ["typeA", "typeB"]

    @property
    def phases(self):
        return [ProcessingPhase.EMBED]

    def process(self, properties, current_file_dir, processing_stack, context=None):
        return f"MockA processed {properties.get('source', 'nothing')}"


class MockPluginB(EmbedPlugin):
    """Another mock plugin."""
    @property
    def name(self):
        return "mock_b"

    @property
    def embed_types(self):
        return ["typeC"]

    @property
    def phases(self):
        return [ProcessingPhase.POST_PROCESS]

    def process(self, properties, current_file_dir, processing_stack, context=None):
        return f"MockB processed {properties.get('content', 'nothing')}"


class MockMultiPhasePlugin(EmbedPlugin):
    """Plugin that runs in multiple phases."""
    @property
    def name(self):
        return "mock_multi"

    @property
    def embed_types(self):
        return ["multi"]

    @property
    def phases(self):
        return [ProcessingPhase.EMBED, ProcessingPhase.POST_PROCESS]

    def process(self, properties, current_file_dir, processing_stack, context=None):
        return "MultiPhase processed"


class TestPluginRegistry:
    """Test PluginRegistry functionality."""

    def test_registry_initialization(self):
        """Test registry initializes empty."""
        registry = PluginRegistry()
        assert len(registry.get_all_plugins()) == 0

    def test_register_single_plugin(self):
        """Test registering a single plugin."""
        registry = PluginRegistry()
        plugin = MockPluginA()

        registry.register(plugin)

        assert len(registry.get_all_plugins()) == 1
        assert registry.get_plugin("typeA", ProcessingPhase.EMBED) == plugin
        assert registry.get_plugin("typeB", ProcessingPhase.EMBED) == plugin

    def test_register_multiple_plugins(self):
        """Test registering multiple plugins."""
        registry = PluginRegistry()
        pluginA = MockPluginA()
        pluginB = MockPluginB()

        registry.register(pluginA)
        registry.register(pluginB)

        assert len(registry.get_all_plugins()) == 2
        assert registry.get_plugin("typeA", ProcessingPhase.EMBED) == pluginA
        assert registry.get_plugin("typeC", ProcessingPhase.POST_PROCESS) == pluginB

    def test_register_multi_phase_plugin(self):
        """Test plugin registered for multiple phases."""
        registry = PluginRegistry()
        plugin = MockMultiPhasePlugin()

        registry.register(plugin)

        # Should be registered in both phases
        assert registry.get_plugin("multi", ProcessingPhase.EMBED) == plugin
        assert registry.get_plugin("multi", ProcessingPhase.POST_PROCESS) == plugin

    def test_register_conflict_raises_error(self):
        """Test conflicting registration raises ValueError."""
        registry = PluginRegistry()
        pluginA = MockPluginA()

        # Create conflicting plugin
        class ConflictPlugin(EmbedPlugin):
            @property
            def name(self):
                return "conflict"

            @property
            def embed_types(self):
                return ["typeA"]  # Conflicts with MockPluginA

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                return ""

        conflict = ConflictPlugin()

        registry.register(pluginA)
        with pytest.raises(ValueError, match="conflicts"):
            registry.register(conflict)

    def test_get_plugin_returns_none_if_not_registered(self):
        """Test get_plugin returns None for unregistered type."""
        registry = PluginRegistry()

        result = registry.get_plugin("unknown", ProcessingPhase.EMBED)

        assert result is None

    def test_get_plugins_for_phase(self):
        """Test getting all plugins for specific phase."""
        registry = PluginRegistry()
        pluginA = MockPluginA()  # EMBED phase
        pluginB = MockPluginB()  # POST_PROCESS phase

        registry.register(pluginA)
        registry.register(pluginB)

        embed_plugins = registry.get_plugins_for_phase(ProcessingPhase.EMBED)
        post_plugins = registry.get_plugins_for_phase(ProcessingPhase.POST_PROCESS)

        assert len(embed_plugins) == 1
        assert pluginA in embed_plugins
        assert len(post_plugins) == 1
        assert pluginB in post_plugins

    def test_is_registered(self):
        """Test is_registered check."""
        registry = PluginRegistry()
        plugin = MockPluginA()

        assert not registry.is_registered("typeA", ProcessingPhase.EMBED)

        registry.register(plugin)

        assert registry.is_registered("typeA", ProcessingPhase.EMBED)
        assert registry.is_registered("typeB", ProcessingPhase.EMBED)
        assert not registry.is_registered("typeA", ProcessingPhase.POST_PROCESS)


class TestDispatcher:
    """Test dispatch_embed function."""

    def test_dispatch_to_registered_plugin(self):
        """Test dispatcher routes to registered plugin."""
        registry = PluginRegistry()
        plugin = MockPluginA()
        registry.register(plugin)

        result = dispatch_embed(
            "typeA",
            {"source": "test.txt"},
            "/dir",
            set(),
            registry=registry,
            phase=ProcessingPhase.EMBED
        )

        assert "MockA processed test.txt" in result

    def test_dispatch_to_fallback_file_handler(self, tmp_path):
        """Test dispatcher falls back to process_file_embed."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = dispatch_embed(
            "file",
            {"source": "test.txt"},
            str(tmp_path),
            set(),
            registry=PluginRegistry(),  # Empty registry
            phase=ProcessingPhase.EMBED
        )

        # Should use fallback handler
        assert "```" in result
        assert "content" in result

    def test_dispatch_unknown_type_returns_error(self):
        """Test dispatcher returns error for unknown type."""
        result = dispatch_embed(
            "unknown_type",
            {},
            "/dir",
            set(),
            registry=PluginRegistry(),
            phase=ProcessingPhase.EMBED
        )

        assert "Unknown embed type" in result
        assert "unknown_type" in result

    def test_dispatch_comment_returns_empty(self):
        """Test dispatcher returns empty string for comments."""
        result = dispatch_embed(
            "comment",
            {},
            "/dir",
            set(),
            registry=PluginRegistry(),
            phase=ProcessingPhase.EMBED
        )

        assert result == ''

    def test_dispatch_uses_default_registry_if_none(self):
        """Test dispatcher uses default registry when none provided."""
        # Register in default registry
        default_reg = get_default_registry()
        plugin = MockPluginA()
        default_reg.register(plugin)

        result = dispatch_embed(
            "typeA",
            {"source": "file.txt"},
            "/dir",
            set(),
            phase=ProcessingPhase.EMBED
            # No registry parameter - should use default
        )

        assert "MockA processed" in result

        # Clean up
        set_default_registry(PluginRegistry())


class TestDefaultRegistry:
    """Test default registry management."""

    def test_get_default_registry_creates_singleton(self):
        """Test default registry is singleton."""
        reg1 = get_default_registry()
        reg2 = get_default_registry()

        assert reg1 is reg2

    def test_set_default_registry(self):
        """Test setting custom default registry."""
        custom = PluginRegistry()
        plugin = MockPluginA()
        custom.register(plugin)

        set_default_registry(custom)

        default = get_default_registry()
        assert default is custom
        assert len(default.get_all_plugins()) == 1

        # Clean up
        set_default_registry(PluginRegistry())
