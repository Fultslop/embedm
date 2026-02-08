"""Tests for FilePlugin."""

import pytest
from embedm_plugins.file_plugin import FilePlugin
from embedm.phases import ProcessingPhase


class TestFilePlugin:
    """Test FilePlugin implementation."""

    def test_plugin_metadata(self):
        """Test plugin provides correct metadata."""
        plugin = FilePlugin()

        assert plugin.name == "file"
        assert "file" in plugin.embed_types
        assert "embed" in plugin.embed_types  # Legacy alias
        assert ProcessingPhase.EMBED in plugin.phases

    def test_process_file_embed(self, tmp_path):
        """Test basic file embedding."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    print('world')")

        # Create plugin and process
        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Verify result
        assert "```py" in result
        assert "def hello():" in result
        assert "print('world')" in result

    def test_process_file_with_line_range(self, tmp_path):
        """Test file embedding with line range."""
        # Create test file with multiple lines
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")

        # Process with line range
        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "region": "L2-4"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should only contain lines 2-4
        assert "line2" in result
        assert "line3" in result
        assert "line4" in result
        assert "line1" not in result
        assert "line5" not in result

    def test_process_file_with_title(self, tmp_path):
        """Test file embedding with title."""
        test_file = tmp_path / "test.py"
        test_file.write_text("code here")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "title": "My Code"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "**My Code**" in result
        assert "code here" in result

    def test_process_missing_file(self, tmp_path):
        """Test error handling for missing file."""
        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "nonexistent.py"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should return error message
        assert "> [!CAUTION]" in result
        assert "File not found" in result or "not found" in result.lower()

    def test_process_missing_source_property(self, tmp_path):
        """Test error handling for missing source property."""
        plugin = FilePlugin()
        result = plugin.process(
            properties={},  # Missing 'source'
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should return error message
        assert "> [!CAUTION]" in result
        assert "source" in result.lower()


class TestFilePluginIntegration:
    """Test FilePlugin integration with registry."""

    def test_plugin_can_be_registered(self):
        """Test plugin can be registered in registry."""
        from embedm.registry import PluginRegistry

        registry = PluginRegistry()
        plugin = FilePlugin()

        # Should register without error
        registry.register(plugin)

        # Should be retrievable
        retrieved = registry.get_plugin("file", ProcessingPhase.EMBED)
        assert retrieved is plugin

        # Legacy alias should also work
        retrieved_legacy = registry.get_plugin("embed", ProcessingPhase.EMBED)
        assert retrieved_legacy is plugin

    def test_plugin_works_with_dispatcher(self, tmp_path):
        """Test plugin works through dispatcher."""
        from embedm.registry import PluginRegistry, dispatch_embed

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Register plugin
        registry = PluginRegistry()
        plugin = FilePlugin()
        registry.register(plugin)

        # Dispatch through registry
        result = dispatch_embed(
            embed_type="file",
            properties={"source": "test.txt"},
            current_file_dir=str(tmp_path),
            processing_stack=set(),
            phase=ProcessingPhase.EMBED,
            registry=registry
        )

        assert "test content" in result
