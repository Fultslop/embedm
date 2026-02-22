import pytest

from embedm.parsing.extraction import extract_line_range, extract_region, is_valid_line_range

# ---------------------------------------------------------------------------
# extract_region
# ---------------------------------------------------------------------------

_CS_SOURCE = """\
public class Foo
{
    // md.start: doSomething
    public void doSomething()
    {
        // ...
    }
    // md.end: doSomething

    public void other() {}
}
"""

_PY_SOURCE = """\
class Foo:
    # md.start: bar
    def bar(self):
        pass
    # md.end: bar
"""

_HTML_SOURCE = """\
<!-- md.start: snippet -->
<p>Hello</p>
<!-- md.end: snippet -->
"""


def test_extract_region_csharp_comment():
    lines = extract_region(_CS_SOURCE, "doSomething")
    assert lines is not None
    assert any("doSomething" in l for l in lines)
    assert not any("md.start" in l for l in lines)
    assert not any("md.end" in l for l in lines)


def test_extract_region_python_comment():
    lines = extract_region(_PY_SOURCE, "bar")
    assert lines is not None
    assert any("def bar" in l for l in lines)


def test_extract_region_html_comment():
    lines = extract_region(_HTML_SOURCE, "snippet")
    assert lines is not None
    assert any("<p>Hello</p>" in l for l in lines)


def test_extract_region_not_found():
    assert extract_region(_CS_SOURCE, "nonexistent") is None


def test_extract_region_case_insensitive_marker():
    source = "// MD.START: myRegion\ncontent\n// MD.END: myRegion\n"
    lines = extract_region(source, "myRegion")
    assert lines is not None
    assert lines == ["content"]


def test_extract_region_missing_end_returns_none():
    source = "// md.start: open\ncontent\n"
    assert extract_region(source, "open") is None


def test_extract_region_wrong_name_ignored():
    source = "// md.start: other\ncontent\n// md.end: other\n"
    assert extract_region(source, "missing") is None


def test_extract_region_crlf_line_endings():
    source = "// md.start: r\r\nline\r\n// md.end: r\r\n"
    lines = extract_region(source, "r")
    assert lines == ["line"]


def test_extract_region_empty_body():
    source = "// md.start: empty\n// md.end: empty\n"
    lines = extract_region(source, "empty")
    assert lines == []


def test_extract_region_custom_templates():
    source = "// region:myblock\ncontent line\n// endregion:myblock\n"
    lines = extract_region(source, "myblock", start_template="region:{tag}", end_template="endregion:{tag}")
    assert lines == ["content line"]


def test_extract_region_default_templates_still_work():
    lines = extract_region(_CS_SOURCE, "doSomething")
    assert lines is not None
    assert any("doSomething" in l for l in lines)


def test_extract_region_custom_template_not_found_with_default_marker():
    # Custom template should not match the default md.start marker
    source = "// md.start: foo\ncontent\n// md.end: foo\n"
    lines = extract_region(source, "foo", start_template="region:{tag}", end_template="endregion:{tag}")
    assert lines is None


# ---------------------------------------------------------------------------
# extract_line_range
# ---------------------------------------------------------------------------

_CONTENT = "line1\nline2\nline3\nline4\nline5\n"


def test_extract_single_line():
    assert extract_line_range(_CONTENT, "2") == ["line2"]


def test_extract_range_inclusive():
    assert extract_line_range(_CONTENT, "2..4") == ["line2", "line3", "line4"]


def test_extract_from_line_to_end():
    assert extract_line_range(_CONTENT, "4..") == ["line4", "line5", ""]


def test_extract_from_start_to_line():
    assert extract_line_range(_CONTENT, "..3") == ["line1", "line2", "line3"]


def test_extract_full_range():
    assert extract_line_range(_CONTENT, "1..5") == ["line1", "line2", "line3", "line4", "line5"]


def test_extract_single_line_out_of_bounds():
    assert extract_line_range(_CONTENT, "99") is None


def test_extract_invalid_format_returns_none():
    assert extract_line_range(_CONTENT, "1-5") is None
    assert extract_line_range(_CONTENT, "abc") is None
    assert extract_line_range(_CONTENT, "") is None


def test_extract_start_greater_than_end_returns_none():
    assert extract_line_range(_CONTENT, "4..2") is None


def test_extract_start_beyond_file_returns_none():
    assert extract_line_range(_CONTENT, "99..") is None


def test_extract_crlf_content():
    content = "a\r\nb\r\nc\r\n"
    assert extract_line_range(content, "2") == ["b"]


# ---------------------------------------------------------------------------
# is_valid_line_range
# ---------------------------------------------------------------------------


def test_valid_single():
    assert is_valid_line_range("10")


def test_valid_range():
    assert is_valid_line_range("5..10")


def test_valid_open_end():
    assert is_valid_line_range("10..")


def test_valid_open_start():
    assert is_valid_line_range("..10")


def test_valid_open_both():
    assert is_valid_line_range("..")


def test_invalid_dash_syntax():
    assert not is_valid_line_range("5-10")


def test_invalid_alpha():
    assert not is_valid_line_range("abc")


def test_invalid_empty():
    assert not is_valid_line_range("")
