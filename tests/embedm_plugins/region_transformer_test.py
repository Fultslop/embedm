from embedm_plugins.file.region_transformer import RegionParams, RegionTransformer


def _run(content: str, region: str) -> str | None:
    return RegionTransformer().execute(RegionParams(content=content, region_name=region))


def test_extract_existing_region():
    source = "// md.start: foo\nline1\nline2\n// md.end: foo\n"
    assert _run(source, "foo") == "line1\nline2"


def test_region_not_found_returns_none():
    assert _run("// md.start: other\n...\n// md.end: other\n", "missing") is None


def test_empty_region_body():
    source = "// md.start: empty\n// md.end: empty\n"
    assert _run(source, "empty") == ""


def test_missing_end_marker_returns_none():
    assert _run("// md.start: open\ncontent\n", "open") is None


def test_custom_template_matches_custom_marker():
    source = "// region:myblock\nline1\n// endregion:myblock\n"
    result = RegionTransformer().execute(
        RegionParams(
            content=source,
            region_name="myblock",
            region_start_template="region:{tag}",
            region_end_template="endregion:{tag}",
        )
    )
    assert result == "line1"


def test_default_template_unchanged():
    source = "# md.start: py\ndef foo(): pass\n# md.end: py\n"
    result = RegionTransformer().execute(RegionParams(content=source, region_name="py"))
    assert result == "def foo(): pass"
