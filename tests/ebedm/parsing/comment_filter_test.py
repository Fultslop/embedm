"""Tests for comment_filter — covers Python and C-style comment removal."""

from embedm.parsing.comment_filter import filter_comments
from embedm.parsing.symbol_parser import CommentStyle

_PYTHON_STYLE = CommentStyle(line_comment="#", string_delimiters=['"', "'"])
_C_STYLE = CommentStyle(
    line_comment="//",
    block_comment_start="/*",
    block_comment_end="*/",
    string_delimiters=['"', "'"],
)
_NO_COMMENT_STYLE = CommentStyle()


# ---------------------------------------------------------------------------
# Python — full-line comments
# ---------------------------------------------------------------------------


def test_py_full_line_comment_dropped():
    src = "# comment\nx = 1"
    assert filter_comments(src, _PYTHON_STYLE) == "x = 1"


def test_py_indented_full_line_comment_dropped():
    src = "class Foo:\n    # a note\n    x: int = 0"
    assert filter_comments(src, _PYTHON_STYLE) == "class Foo:\n    x: int = 0"


def test_py_multiple_full_line_comments_dropped():
    src = "# first\n# second\nx = 1"
    assert filter_comments(src, _PYTHON_STYLE) == "x = 1"


# ---------------------------------------------------------------------------
# Python — trailing inline comments
# ---------------------------------------------------------------------------


def test_py_trailing_comment_stripped():
    src = "x = 1  # inline note"
    assert filter_comments(src, _PYTHON_STYLE) == "x = 1"


def test_py_trailing_comment_rstripped():
    src = "x = 1   # note"
    assert filter_comments(src, _PYTHON_STYLE) == "x = 1"


def test_py_string_with_hash_not_mangled():
    src = 'url = "http://foo"'
    assert filter_comments(src, _PYTHON_STYLE) == src


def test_py_string_with_hash_then_trailing_comment():
    src = 'url = "http://foo"  # note'
    assert filter_comments(src, _PYTHON_STYLE) == 'url = "http://foo"'


# ---------------------------------------------------------------------------
# Python — blank lines and no-op cases
# ---------------------------------------------------------------------------


def test_py_blank_lines_preserved():
    src = "x = 1\n\ny = 2"
    assert filter_comments(src, _PYTHON_STYLE) == src


def test_py_no_comments_unchanged():
    src = "x = 1\ny = 2\nz = x + y"
    assert filter_comments(src, _PYTHON_STYLE) == src


def test_py_spec_example():
    """The motivating example from the spec."""
    src = (
        "class Directive:\n"
        "    type: str\n"
        "    # source file, may be None if a directive does not use an input file\n"
        "    # eg ToC\n"
        "    source: str = \"\"\n"
        "    options: dict[str, str] = field(default_factory=dict)\n"
        "    # directory of the file that contains this directive\n"
        "    base_dir: str = \"\"\n"
    )
    expected = (
        "class Directive:\n"
        "    type: str\n"
        "    source: str = \"\"\n"
        "    options: dict[str, str] = field(default_factory=dict)\n"
        "    base_dir: str = \"\"\n"
    )
    assert filter_comments(src, _PYTHON_STYLE) == expected


# ---------------------------------------------------------------------------
# C-style — full-line // comments
# ---------------------------------------------------------------------------


def test_c_full_line_comment_dropped():
    src = "// comment\nint x = 1;"
    assert filter_comments(src, _C_STYLE) == "int x = 1;"


def test_c_trailing_comment_stripped():
    src = "int x = 1; // inline note"
    assert filter_comments(src, _C_STYLE) == "int x = 1;"


def test_c_string_with_slashes_not_mangled():
    src = 'char* s = "http://foo";'
    assert filter_comments(src, _C_STYLE) == src


# ---------------------------------------------------------------------------
# C-style — block comments
# ---------------------------------------------------------------------------


def test_c_block_comment_single_line_dropped():
    src = "/* comment */\nint x = 1;"
    assert filter_comments(src, _C_STYLE) == "int x = 1;"


def test_c_block_comment_multiline_dropped():
    src = "/*\n * comment\n */\nint x = 1;"
    assert filter_comments(src, _C_STYLE) == "int x = 1;"


def test_c_block_comment_trailing_stripped():
    src = "int x = 1; /* note */"
    assert filter_comments(src, _C_STYLE) == "int x = 1;"


def test_c_blank_lines_between_block_comment_and_code_preserved():
    src = "/*\n * doc\n */\n\nint x = 1;"
    assert filter_comments(src, _C_STYLE) == "\nint x = 1;"


# ---------------------------------------------------------------------------
# No comment style — content passes through unchanged
# ---------------------------------------------------------------------------


def test_no_comment_style_unchanged():
    src = "# not a comment\n// also not\nsome content"
    assert filter_comments(src, _NO_COMMENT_STYLE) == src
