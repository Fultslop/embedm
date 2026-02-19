from pathlib import Path

from embedm.domain.directive import Directive
from embedm.domain.span import Span
from embedm.domain.status_level import Status, StatusLevel
from embedm.parsing.directive_parser import (
    find_yaml_embed_block,
    parse_yaml_embed_block,
    parse_yaml_embed_blocks,
)


def _span_text(content: str, span: Span) -> str:
    """Extract text from content using a Span."""
    return content[span.offset : span.offset + span.length]


# --- parse_yaml_embed_block: happy path ---


def test_parse_block_type_only():
    yaml_content = "type: hello_world"
    directive, errors = parse_yaml_embed_block(yaml_content)

    assert directive == Directive(type="hello_world")
    assert errors == []


def test_parse_block_with_source():
    yaml_content = "type: file_embed\nsource: myfile.py"
    directive, errors = parse_yaml_embed_block(yaml_content)

    assert directive == Directive(type="file_embed", source="myfile.py")
    assert errors == []


def test_parse_block_with_options():
    yaml_content = "type: file_embed\nsource: myfile.py\nlines: 1-10\nlanguage: python"
    directive, errors = parse_yaml_embed_block(yaml_content)

    assert directive == Directive(
        type="file_embed",
        source="myfile.py",
        options={"lines": "1-10", "language": "python"},
    )
    assert errors == []


# --- parse_yaml_embed_block: error cases ---


def test_parse_block_empty_string():
    directive, errors = parse_yaml_embed_block("")

    assert directive is None
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_parse_block_missing_type():
    directive, errors = parse_yaml_embed_block("source: myfile.py")

    assert directive is None
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_parse_block_invalid_yaml():
    yaml_content = 'type: some_type\nforget_to_add_colon "value"\n: "no_key"\n#@#@:\n'
    directive, errors = parse_yaml_embed_block(yaml_content)

    assert directive is None
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


# --- find_yaml_embed_block: happy path ---


def test_find_block_returns_match():
    content = "Some text before\n```yaml embedm\ntype: hello_world\n```\n\nSome text after\n"
    result = find_yaml_embed_block(content)

    assert result is not None
    assert result.raw_content == "type: hello_world\n"
    assert result.start == content.index("```yaml embedm\n")
    assert result.end == content.index("```\n\nSome text after\n") + len("```\n")


# --- find_yaml_embed_block: edge cases ---


def test_find_block_returns_none_when_no_block():
    result = find_yaml_embed_block("Just some regular markdown\nwith no embedm blocks\n")
    assert result is None


def test_find_block_empty_string():
    result = find_yaml_embed_block("")
    assert result is None


def test_find_block_unclosed_fence():
    content = "Some text\n```yaml embedm\ntype: hello_world\n"
    result = find_yaml_embed_block(content)
    assert result is None


def test_find_block_ignores_non_embedm_fence():
    content = "```yaml\nkey: value\n```\n"
    result = find_yaml_embed_block(content)
    assert result is None


def test_find_block_empty_embedm_block():
    content = "```yaml embedm\n```\n"
    result = find_yaml_embed_block(content)

    assert result is not None
    assert result.raw_content == ""


# --- parse_yaml_embed_blocks: happy path ---


def test_parse_blocks_single_block():
    content = "Text before\n```yaml embedm\ntype: hello_world\n```\nText after\n"
    fragments, errors = parse_yaml_embed_blocks(content)

    assert errors == []
    assert len(fragments) == 3
    assert isinstance(fragments[0], Span)
    assert _span_text(content, fragments[0]) == "Text before\n"
    assert fragments[1] == Directive(type="hello_world")
    assert isinstance(fragments[2], Span)
    assert _span_text(content, fragments[2]) == "Text after\n"


def test_parse_blocks_multiple_blocks():
    content = (
        "Intro\n"
        "```yaml embedm\n"
        "type: hello_world\n"
        "```\n"
        "Middle\n"
        "```yaml embedm\n"
        "type: file_embed\n"
        "source: example.py\n"
        "```\n"
        "End\n"
    )
    fragments, errors = parse_yaml_embed_blocks(content)

    assert errors == []
    assert len(fragments) == 5
    assert isinstance(fragments[0], Span)
    assert _span_text(content, fragments[0]) == "Intro\n"
    assert fragments[1] == Directive(type="hello_world")
    assert isinstance(fragments[2], Span)
    assert _span_text(content, fragments[2]) == "Middle\n"
    assert fragments[3] == Directive(type="file_embed", source="example.py")
    assert isinstance(fragments[4], Span)
    assert _span_text(content, fragments[4]) == "End\n"


def test_parse_blocks_no_blocks():
    content = "Just plain markdown\nwith no embeds\n"
    fragments, errors = parse_yaml_embed_blocks(content)

    assert errors == []
    assert len(fragments) == 1
    assert isinstance(fragments[0], Span)
    assert _span_text(content, fragments[0]) == content


# --- parse_yaml_embed_blocks: edge cases ---


def test_parse_blocks_empty_string():
    fragments, errors = parse_yaml_embed_blocks("")

    assert errors == []
    assert fragments == []


def test_parse_blocks_block_at_start():
    content = "```yaml embedm\ntype: hello_world\n```\nText after\n"
    fragments, errors = parse_yaml_embed_blocks(content)

    assert errors == []
    assert len(fragments) == 2
    assert fragments[0] == Directive(type="hello_world")
    assert isinstance(fragments[1], Span)
    assert _span_text(content, fragments[1]) == "Text after\n"


def test_parse_blocks_block_at_end():
    content = "Text before\n```yaml embedm\ntype: hello_world\n```\n"
    fragments, errors = parse_yaml_embed_blocks(content)

    assert errors == []
    assert len(fragments) == 2
    assert isinstance(fragments[0], Span)
    assert _span_text(content, fragments[0]) == "Text before\n"
    assert fragments[1] == Directive(type="hello_world")


# --- parse_yaml_embed_blocks: error recovery ---


def test_parse_blocks_unclosed_fence_reports_error():
    content = "Text before\n```yaml embedm\ntype: hello_world\n"
    fragments, errors = parse_yaml_embed_blocks(content)

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert len(fragments) == 1
    assert isinstance(fragments[0], Span)
    assert _span_text(content, fragments[0]) == "Text before\n"


def test_parse_blocks_missing_type_reports_error():
    content = "Text before\n```yaml embedm\nsource: myfile.py\n```\nText after\n"
    fragments, errors = parse_yaml_embed_blocks(content)

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert len(fragments) == 2
    assert isinstance(fragments[0], Span)
    assert _span_text(content, fragments[0]) == "Text before\n"
    assert isinstance(fragments[1], Span)
    assert _span_text(content, fragments[1]) == "Text after\n"


def test_parse_blocks_skips_invalid_continues_to_valid():
    content = (
        "Intro\n```yaml embedm\nsource: missing_type.py\n```\nMiddle\n```yaml embedm\ntype: hello_world\n```\nEnd\n"
    )
    fragments, errors = parse_yaml_embed_blocks(content)

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert len(fragments) == 4
    assert isinstance(fragments[0], Span)
    assert _span_text(content, fragments[0]) == "Intro\n"
    assert isinstance(fragments[1], Span)
    assert _span_text(content, fragments[1]) == "Middle\n"
    assert fragments[2] == Directive(type="hello_world")
    assert isinstance(fragments[3], Span)
    assert _span_text(content, fragments[3]) == "End\n"


# --- parse_yaml_embed_block: base_dir resolution ---


def test_parse_block_resolves_relative_source_against_base_dir(tmp_path: Path):
    base_dir = str(tmp_path / "docs")
    yaml_content = "type: file_embed\nsource: ./chapter.md"

    directive, errors = parse_yaml_embed_block(yaml_content, base_dir=base_dir)

    assert errors == []
    assert directive is not None
    expected = str((tmp_path / "docs" / "chapter.md").resolve())
    assert directive.source == expected


def test_parse_block_leaves_absolute_source_unchanged(tmp_path: Path):
    absolute_path = str(tmp_path / "absolute.md")
    yaml_content = f"type: file_embed\nsource: {absolute_path}"

    directive, errors = parse_yaml_embed_block(yaml_content, base_dir=str(tmp_path / "other"))

    assert errors == []
    assert directive is not None
    assert directive.source == absolute_path


def test_parse_block_no_base_dir_leaves_relative_source():
    yaml_content = "type: file_embed\nsource: ./relative.md"

    directive, errors = parse_yaml_embed_block(yaml_content)

    assert errors == []
    assert directive is not None
    assert directive.source == "./relative.md"


# --- parse_yaml_embed_blocks: base_dir resolution ---


def test_parse_blocks_resolves_sources_with_base_dir(tmp_path: Path):
    base_dir = str(tmp_path / "docs")
    content = "Intro\n```yaml embedm\ntype: file_embed\nsource: ./chapter.md\n```\n"

    fragments, errors = parse_yaml_embed_blocks(content, base_dir=base_dir)

    assert errors == []
    directive = fragments[1]
    assert isinstance(directive, Directive)
    expected = str((tmp_path / "docs" / "chapter.md").resolve())
    assert directive.source == expected


# --- Directive.get_option / validate_option: bool casting ---
# Options are stored as strings by the parser (str(v)), so YAML `true` becomes "True".


def test_directive_get_option_bool_true_string():
    d = Directive(type="toc", options={"flag": "True"})
    assert d.get_option("flag", cast=bool, default_value=False) is True


def test_directive_get_option_bool_false_string():
    d = Directive(type="toc", options={"flag": "False"})
    assert d.get_option("flag", cast=bool, default_value=True) is False


def test_directive_validate_option_bool_invalid_string_returns_error():
    d = Directive(type="toc", options={"flag": "yes"})
    result = d.validate_option("flag", cast=bool)
    assert isinstance(result, Status)
    assert result.level == StatusLevel.ERROR
    assert "flag" in result.description


def test_directive_validate_option_returns_none_when_absent():
    d = Directive(type="toc", options={})
    assert d.validate_option("flag", cast=bool) is None


def test_directive_validate_option_returns_none_when_valid():
    d = Directive(type="toc", options={"flag": "True"})
    assert d.validate_option("flag", cast=bool) is None
