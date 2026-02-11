"""Tests for LayoutPlugin and TOCPlugin."""

import pytest
from embedm_plugins.layout_plugin import LayoutPlugin
from embedm_plugins.toc_plugin import TOCPlugin
from embedm.phases import ProcessingPhase


class TestLayoutPlugin:
    """Test LayoutPlugin implementation."""

    def test_plugin_metadata(self):
        """Test plugin provides correct metadata."""
        plugin = LayoutPlugin()

        assert plugin.name == "layout"
        assert "layout" in plugin.embed_types
        assert ProcessingPhase.EMBED in plugin.phases

    def test_process_layout_embed(self, tmp_path):
        """Test basic layout embedding."""
        # Create test files
        file1 = tmp_path / "file1.txt"
        file1.write_text("Content 1")

        file2 = tmp_path / "file2.txt"
        file2.write_text("Content 2")

        # Create plugin and process
        plugin = LayoutPlugin()
        result = plugin.process(
            properties={
                "orientation": "row",
                "sections": [
                    {"embed": {"type": "embed.file", "source": "file1.txt"}},
                    {"embed": {"type": "embed.file", "source": "file2.txt"}}
                ]
            },
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Verify layout structure
        assert "<div" in result
        assert "Content 1" in result
        assert "Content 2" in result

    def test_process_invalid_layout(self, tmp_path):
        """Test error handling for invalid layout."""
        plugin = LayoutPlugin()
        result = plugin.process(
            properties={},  # Missing 'rows'
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should return error message
        assert "> [!CAUTION]" in result


class TestTOCPlugin:
    """Test TOCPlugin implementation."""

    def test_plugin_metadata(self):
        """Test plugin provides correct metadata."""
        plugin = TOCPlugin()

        assert plugin.name == "toc"
        assert "toc" in plugin.embed_types
        assert "table_of_contents" in plugin.embed_types  # Legacy alias
        assert ProcessingPhase.POST_PROCESS in plugin.phases

    def test_process_toc_from_file(self, tmp_path):
        """Test TOC generation from external file."""
        # Create test markdown file with headings
        doc_file = tmp_path / "document.md"
        doc_file.write_text(
            "# Main Title\n\n"
            "Content here.\n\n"
            "## Section 1\n\n"
            "More content.\n\n"
            "## Section 2\n\n"
            "Final content.\n"
        )

        # Generate TOC
        plugin = TOCPlugin()
        result = plugin.process(
            properties={"source": "document.md"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Verify TOC structure
        assert "- [Main Title](#main-title)" in result
        assert "- [Section 1](#section-1)" in result
        assert "- [Section 2](#section-2)" in result

    def test_process_toc_without_source(self):
        """Test TOC without source returns None (requires special handling)."""
        plugin = TOCPlugin()
        result = plugin.process(
            properties={},  # No source
            current_file_dir="/tmp",
            processing_stack=set()
        )

        # Should return None to signal special handling needed
        assert result is None

    def test_process_toc_missing_file(self, tmp_path):
        """Test error handling for missing file."""
        plugin = TOCPlugin()
        result = plugin.process(
            properties={"source": "nonexistent.md"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should return error message
        assert "> [!CAUTION]" in result
        assert "not found" in result.lower()

    def test_process_toc_with_depth(self, tmp_path):
        """Test TOC generation with depth limit from external file."""
        doc_file = tmp_path / "document.md"
        doc_file.write_text(
            "# Main Title\n\n"
            "## Section 1\n\n"
            "### Subsection 1.1\n\n"
            "#### Detail 1.1.1\n\n"
            "## Section 2\n\n"
            "### Subsection 2.1\n\n"
        )

        plugin = TOCPlugin()

        # depth: 2 should include only # and ##
        result = plugin.process(
            properties={"source": "document.md", "depth": 2},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "- [Main Title](#main-title)" in result
        assert "- [Section 1](#section-1)" in result
        assert "- [Section 2](#section-2)" in result
        assert "Subsection" not in result
        assert "Detail" not in result

    def test_process_toc_depth_includes_up_to_level(self, tmp_path):
        """Test that depth: 3 includes h1, h2, and h3 but not h4."""
        doc_file = tmp_path / "document.md"
        doc_file.write_text(
            "# Title\n\n"
            "## Section\n\n"
            "### Subsection\n\n"
            "#### Detail\n\n"
        )

        plugin = TOCPlugin()
        result = plugin.process(
            properties={"source": "document.md", "depth": 3},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "- [Title](#title)" in result
        assert "- [Section](#section)" in result
        assert "- [Subsection](#subsection)" in result
        assert "Detail" not in result

    def test_process_toc_no_depth_includes_all(self, tmp_path):
        """Test that omitting depth includes all heading levels."""
        doc_file = tmp_path / "document.md"
        doc_file.write_text(
            "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6\n"
        )

        plugin = TOCPlugin()
        result = plugin.process(
            properties={"source": "document.md"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "- [H1](#h1)" in result
        assert "- [H2](#h2)" in result
        assert "- [H3](#h3)" in result
        assert "- [H4](#h4)" in result
        assert "- [H5](#h5)" in result
        assert "- [H6](#h6)" in result


class TestAllPluginsIntegration:
    """Test all plugins together."""

    def test_all_plugins_can_be_registered(self):
        """Test all plugins can be registered together."""
        from embedm.registry import PluginRegistry
        from embedm_plugins import FilePlugin, LayoutPlugin, TOCPlugin

        registry = PluginRegistry()

        # Register all plugins
        registry.register(FilePlugin())
        registry.register(LayoutPlugin())
        registry.register(TOCPlugin())

        # Verify all are registered
        assert registry.get_plugin("file", ProcessingPhase.EMBED) is not None
        assert registry.get_plugin("layout", ProcessingPhase.EMBED) is not None
        assert registry.get_plugin("toc", ProcessingPhase.POST_PROCESS) is not None

    def test_builtin_plugins_auto_registered(self):
        """Test built-in plugins are auto-registered."""
        # Import embedm_plugins triggers auto-registration
        import embedm_plugins
        from embedm.registry import get_default_registry

        registry = get_default_registry()

        # All built-in plugins should be registered
        assert registry.is_registered("file", ProcessingPhase.EMBED)
        assert registry.is_registered("layout", ProcessingPhase.EMBED)
        assert registry.is_registered("toc", ProcessingPhase.POST_PROCESS)

    def test_plugins_work_through_dispatcher(self, tmp_path):
        """Test all plugins work through dispatcher."""
        from embedm.registry import dispatch_embed
        from embedm.phases import ProcessingPhase

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Test file plugin through dispatcher
        result_file = dispatch_embed(
            embed_type="file",
            properties={"source": "test.txt"},
            current_file_dir=str(tmp_path),
            processing_stack=set(),
            phase=ProcessingPhase.EMBED
        )
        assert "test content" in result_file

        # Create markdown for TOC
        doc_file = tmp_path / "doc.md"
        doc_file.write_text("# Title\n")

        # Test TOC plugin through dispatcher
        result_toc = dispatch_embed(
            embed_type="toc",
            properties={"source": "doc.md"},
            current_file_dir=str(tmp_path),
            processing_stack=set(),
            phase=ProcessingPhase.POST_PROCESS
        )
        assert "Title" in result_toc
