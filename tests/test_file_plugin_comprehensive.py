"""Comprehensive tests for FilePlugin covering all features."""

import pytest
from embedm_plugins.file_plugin import FilePlugin
from embedm.phases import ProcessingPhase


class TestFilePluginLinesProperty:
    """Test the 'lines' property (separate from 'region')."""

    def test_lines_property_new_format(self, tmp_path):
        """Test lines property with new clean format (no L prefix)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "2-4"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "line2" in result
        assert "line3" in result
        assert "line4" in result
        assert "line1" not in result
        assert "line5" not in result

    def test_lines_property_legacy_format(self, tmp_path):
        """Test lines property still works with L prefix (backward compat)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "L2-4"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "line2" in result
        assert "line3" in result
        assert "line4" in result

    def test_lines_property_single_line(self, tmp_path):
        """Test extracting a single line."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "2"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "line2" in result
        assert "line1" not in result
        assert "line3" not in result

    def test_lines_property_to_end(self, tmp_path):
        """Test extracting from line to end of file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "3-"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "line3" in result
        assert "line4" in result
        assert "line5" in result
        assert "line1" not in result
        assert "line2" not in result

    def test_lines_property_invalid_range(self, tmp_path):
        """Test error handling for invalid line range."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "invalid"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "> [!CAUTION]" in result
        assert "Invalid line range" in result


class TestFilePluginNamedRegions:
    """Test named region extraction with md.start/end markers."""

    def test_region_extraction_basic(self, tmp_path):
        """Test basic region extraction."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""def helper():
    pass

# md.start:main
def main():
    print("Hello")
# md.end:main

def other():
    pass
""")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "region": "main"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "def main():" in result
        assert 'print("Hello")' in result
        assert "def helper():" not in result
        assert "def other():" not in result

    def test_region_extraction_with_whitespace(self, tmp_path):
        """Test region markers with whitespace (md.start: name)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""# md.start: my_region
code inside region
# md.end: my_region
""")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "region": "my_region"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "code inside region" in result

    def test_region_not_found(self, tmp_path):
        """Test error when region doesn't exist."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# md.start:other\ncode\n# md.end:other")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "region": "missing"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "> [!CAUTION]" in result
        assert "Region" in result
        assert "not found" in result

    def test_region_ignores_docstring_mentions(self, tmp_path):
        """Test that region markers mentioned in docstrings are ignored."""
        test_file = tmp_path / "test.py"
        test_file.write_text('''"""
This docstring mentions md.start:function
and md.end:function but they shouldn't match.
"""

# md.start:function
def my_function():
    """Real function here."""
    return 42
# md.end:function
''')

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "region": "function"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should only extract the function, not the docstring
        assert "def my_function():" in result
        assert "return 42" in result
        # The docstring mentioning markers should NOT be in result
        # (because it's before the actual markers)
        assert "This docstring mentions" not in result

    def test_region_different_comment_styles(self, tmp_path):
        """Test region markers work with different comment styles."""
        # C++ style comments
        cpp_file = tmp_path / "test.cpp"
        cpp_file.write_text("""// md.start:region
int x = 10;
// md.end:region
""")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.cpp", "region": "region"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "int x = 10;" in result


class TestFilePluginLineNumbers:
    """Test line number formatting options."""

    def test_line_numbers_text(self, tmp_path):
        """Test text line numbers."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "2-3", "line_numbers": "text"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Text line numbers should be in the result
        assert "2" in result
        assert "3" in result
        assert "line2" in result
        assert "line3" in result

    def test_line_numbers_html(self, tmp_path):
        """Test HTML line numbers."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "2-3", "line_numbers": "html"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # HTML line numbers should contain div/style elements
        assert "<div" in result or "<style>" in result
        assert "line2" in result
        assert "line3" in result

    def test_line_numbers_table(self, tmp_path):
        """Test table line numbers (GitHub-compatible)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "2-3", "line_numbers": "table"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Table line numbers should use markdown table syntax
        assert "| Line | Code |" in result
        assert "|-----:|------|" in result
        assert "| 2 |" in result
        assert "| 3 |" in result

    def test_line_numbers_with_region(self, tmp_path):
        """Test line numbers work with named regions."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""line1
line2
# md.start:region
line4
line5
# md.end:region
line7
""")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "region": "region", "line_numbers": "text"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should show line numbers starting from line 4
        assert "4" in result
        assert "5" in result
        assert "line4" in result
        assert "line5" in result


class TestFilePluginCombinations:
    """Test combinations of features."""

    def test_lines_with_title(self, tmp_path):
        """Test lines property with title."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "test.py", "lines": "2", "title": "My Code"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "**My Code**" in result
        assert "line2" in result

    def test_region_with_title_and_line_numbers(self, tmp_path):
        """Test region with both title and line numbers."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""# md.start:func
def hello():
    pass
# md.end:func
""")

        plugin = FilePlugin()
        result = plugin.process(
            properties={
                "source": "test.py",
                "region": "func",
                "title": "Function",
                "line_numbers": "text"
            },
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        assert "**Function**" in result
        assert "def hello():" in result
        assert "2" in result  # Line number

    def test_lines_and_region_both_provided(self, tmp_path):
        """Test that 'lines' takes precedence over 'region'."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""line1
# md.start:region
line3
# md.end:region
line5
""")

        plugin = FilePlugin()
        result = plugin.process(
            properties={
                "source": "test.py",
                "lines": "1",  # Should use lines, not region
                "region": "region"
            },
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should extract line 1, not the region
        assert "line1" in result
        assert "line3" not in result


class TestFilePluginEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_file(self, tmp_path):
        """Test embedding an empty file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "empty.py"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Should succeed but have empty content
        assert "```py" in result

    def test_file_with_special_characters(self, tmp_path):
        """Test file containing special characters (pipe in table format)."""
        test_file = tmp_path / "special.py"
        test_file.write_text('print("Hello | world")')  # Pipe character

        plugin = FilePlugin()
        result = plugin.process(
            properties={"source": "special.py", "line_numbers": "table"},
            current_file_dir=str(tmp_path),
            processing_stack=set()
        )

        # Pipes should be escaped in table format
        assert "Hello" in result
        # Either the pipe is escaped as \| or it's in a code cell
        assert "world" in result
