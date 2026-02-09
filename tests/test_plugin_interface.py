"""Tests for plugin interface."""

import os
import pytest
from embedm.plugin import (
    EmbedPlugin,
    get_file_extension,
    wrap_in_code_block,
    wrap_with_title
)
from embedm.phases import ProcessingPhase
from embedm.models import ValidationError


class TestPluginUtilities:
    """Test utility functions."""

    def test_get_file_extension_with_extension(self):
        """Test extension extraction."""
        assert get_file_extension("file.py") == "py"
        assert get_file_extension("path/to/file.txt") == "txt"

    def test_get_file_extension_no_extension(self):
        """Test files without extension."""
        assert get_file_extension("README") == "text"

    def test_wrap_in_code_block_with_language(self):
        """Test code block wrapping with explicit language."""
        result = wrap_in_code_block("print('hi')", language="python")
        assert result == "```python\nprint('hi')\n```"

    def test_wrap_in_code_block_from_file_path(self):
        """Test language detection from file path."""
        result = wrap_in_code_block("def test():", file_path="test.py")
        assert result == "```py\ndef test():\n```"

    def test_wrap_in_code_block_strips_trailing_whitespace(self):
        """Test that trailing whitespace is stripped."""
        result = wrap_in_code_block("content\n\n\n", language="text")
        assert result == "```text\ncontent\n```"

    def test_wrap_with_title_present(self):
        """Test title wrapping when title provided."""
        result = wrap_with_title("content", "My Title")
        assert result == "**My Title**\n\ncontent"

    def test_wrap_with_title_none(self):
        """Test no wrapping when title is None."""
        result = wrap_with_title("content", None)
        assert result == "content"

    def test_wrap_with_title_empty_string(self):
        """Test no wrapping when title is empty string."""
        result = wrap_with_title("content", "")
        assert result == "content"


class MockPlugin(EmbedPlugin):
    """Mock plugin for testing."""

    @property
    def name(self):
        return "mock"

    @property
    def embed_types(self):
        return ["mock", "test"]

    @property
    def phases(self):
        return [ProcessingPhase.EMBED]

    def process(self, properties, current_file_dir, processing_stack, context=None):
        return "mock content"


class TestEmbedPluginInterface:
    """Test EmbedPlugin base class."""

    def test_plugin_has_required_properties(self):
        """Test plugin defines required properties."""
        plugin = MockPlugin()

        assert plugin.name == "mock"
        assert plugin.embed_types == ["mock", "test"]
        assert plugin.phases == [ProcessingPhase.EMBED]

    def test_resolve_path_relative(self, tmp_path):
        """Test relative path resolution."""
        plugin = MockPlugin()

        current_dir = str(tmp_path)
        result = plugin.resolve_path("file.txt", current_dir)

        expected = os.path.join(current_dir, "file.txt")
        assert result == os.path.abspath(expected)

    def test_resolve_path_absolute(self, tmp_path):
        """Test absolute path resolution."""
        plugin = MockPlugin()

        absolute = str(tmp_path / "file.txt")
        result = plugin.resolve_path(absolute, "/some/dir")

        assert result == os.path.abspath(absolute)

    def test_format_error(self):
        """Test error formatting."""
        plugin = MockPlugin()

        error = plugin.format_error("Test Error", "something went wrong")

        assert "> [!CAUTION]" in error
        assert "**Test Error:**" in error
        assert "something went wrong" in error

    def test_check_file_exists_missing(self):
        """Test file existence check for missing file."""
        plugin = MockPlugin()

        error = plugin.check_file_exists("nonexistent.txt")

        assert error is not None
        assert "File Not Found" in error

    def test_check_file_exists_directory(self, tmp_path):
        """Test file existence check for directory."""
        plugin = MockPlugin()

        error = plugin.check_file_exists(str(tmp_path))

        assert error is not None
        assert "Invalid File" in error
        assert "is a directory" in error

    def test_check_file_exists_valid(self, tmp_path):
        """Test file existence check for valid file."""
        plugin = MockPlugin()

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        error = plugin.check_file_exists(str(test_file))

        assert error is None

    def test_check_limit_within_limit(self):
        """Test limit checking when within limit."""
        plugin = MockPlugin()

        error = plugin.check_limit(50, 100, "Size", "50B", "100B")

        assert error is None

    def test_check_limit_exceeds_limit(self):
        """Test limit checking when exceeded."""
        plugin = MockPlugin()

        error = plugin.check_limit(150, 100, "Size", "150B", "100B")

        assert error is not None
        assert "Size Limit Exceeded" in error
        assert "150B" in error
        assert "100B" in error

    def test_check_limit_unlimited(self):
        """Test limit checking with limit=0 (unlimited)."""
        plugin = MockPlugin()

        error = plugin.check_limit(9999, 0, "Size", "9999B", "0B")

        assert error is None

    def test_validate_default_implementation(self):
        """Test default validate() returns empty list."""
        plugin = MockPlugin()

        errors = plugin.validate({}, "/dir", "/file.md", 1)

        assert errors == []

    def test_multi_phase_plugin(self):
        """Test plugin can run in multiple phases."""
        class MultiPhasePlugin(EmbedPlugin):
            @property
            def name(self):
                return "multi"

            @property
            def embed_types(self):
                return ["multi"]

            @property
            def phases(self):
                return [ProcessingPhase.EMBED, ProcessingPhase.POST_PROCESS]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                return "multi phase content"

        plugin = MultiPhasePlugin()
        assert ProcessingPhase.EMBED in plugin.phases
        assert ProcessingPhase.POST_PROCESS in plugin.phases
        assert len(plugin.phases) == 2


class TestPluginAbstractMethods:
    """Test that abstract methods must be implemented."""

    def test_cannot_instantiate_base_class(self):
        """Test EmbedPlugin cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmbedPlugin()

    def test_missing_name_raises_error(self):
        """Test plugin must implement name property."""
        class IncompletePlugin(EmbedPlugin):
            @property
            def embed_types(self):
                return ["test"]

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                return ""

        with pytest.raises(TypeError):
            IncompletePlugin()

    def test_missing_embed_types_raises_error(self):
        """Test plugin must implement embed_types property."""
        class IncompletePlugin(EmbedPlugin):
            @property
            def name(self):
                return "test"

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                return ""

        with pytest.raises(TypeError):
            IncompletePlugin()

    def test_missing_phases_raises_error(self):
        """Test plugin must implement phases property."""
        class IncompletePlugin(EmbedPlugin):
            @property
            def name(self):
                return "test"

            @property
            def embed_types(self):
                return ["test"]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                return ""

        with pytest.raises(TypeError):
            IncompletePlugin()

    def test_missing_process_raises_error(self):
        """Test plugin must implement process method."""
        class IncompletePlugin(EmbedPlugin):
            @property
            def name(self):
                return "test"

            @property
            def embed_types(self):
                return ["test"]

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

        with pytest.raises(TypeError):
            IncompletePlugin()


class TestPluginProcessMethod:
    """Test plugin process method signature."""

    def test_process_receives_all_parameters(self):
        """Test process method receives correct parameters."""
        class TestPlugin(EmbedPlugin):
            received_args = None

            @property
            def name(self):
                return "test"

            @property
            def embed_types(self):
                return ["test"]

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                TestPlugin.received_args = (properties, current_file_dir, processing_stack, context)
                return "result"

        plugin = TestPlugin()
        props = {'source': 'test.txt'}
        current_dir = '/path/to/dir'
        stack = {'file1.md'}

        result = plugin.process(props, current_dir, stack)

        assert result == "result"
        assert TestPlugin.received_args[0] == props
        assert TestPlugin.received_args[1] == current_dir
        assert TestPlugin.received_args[2] == stack
        assert TestPlugin.received_args[3] is None


class TestRealWorldPluginExample:
    """Test a realistic plugin implementation."""

    def test_simple_file_reader_plugin(self, tmp_path):
        """Test a simple plugin that reads files."""
        class SimpleFilePlugin(EmbedPlugin):
            @property
            def name(self):
                return "simplefile"

            @property
            def embed_types(self):
                return ["simplefile"]

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                source = properties.get('source')
                if not source:
                    return self.format_error("Missing Property", "source is required")

                file_path = self.resolve_path(source, current_file_dir)

                error = self.check_file_exists(file_path)
                if error:
                    return error

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return wrap_in_code_block(content, file_path=file_path)
                except Exception as e:
                    return self.format_error("Read Error", str(e))

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    print('world')")

        # Test plugin
        plugin = SimpleFilePlugin()
        properties = {'source': 'test.py'}
        result = plugin.process(properties, str(tmp_path), set())

        assert "```py" in result
        assert "def hello():" in result
        assert "print('world')" in result

    def test_plugin_with_missing_file(self):
        """Test plugin error handling for missing file."""
        class SimpleFilePlugin(EmbedPlugin):
            @property
            def name(self):
                return "simplefile"

            @property
            def embed_types(self):
                return ["simplefile"]

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                source = properties.get('source')
                if not source:
                    return self.format_error("Missing Property", "source is required")

                file_path = self.resolve_path(source, current_file_dir)

                error = self.check_file_exists(file_path)
                if error:
                    return error

                return "success"

        plugin = SimpleFilePlugin()
        properties = {'source': 'nonexistent.txt'}
        result = plugin.process(properties, '/tmp', set())

        assert "File Not Found" in result
        assert "> [!CAUTION]" in result

    def test_plugin_with_missing_property(self):
        """Test plugin error handling for missing property."""
        class SimpleFilePlugin(EmbedPlugin):
            @property
            def name(self):
                return "simplefile"

            @property
            def embed_types(self):
                return ["simplefile"]

            @property
            def phases(self):
                return [ProcessingPhase.EMBED]

            def process(self, properties, current_file_dir, processing_stack, context=None):
                source = properties.get('source')
                if not source:
                    return self.format_error("Missing Property", "source is required")

                return "success"

        plugin = SimpleFilePlugin()
        properties = {}  # Missing 'source'
        result = plugin.process(properties, '/tmp', set())

        assert "Missing Property" in result
        assert "source is required" in result
