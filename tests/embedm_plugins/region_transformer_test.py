from embedm_plugins.region_transformer import RegionParams, RegionTransformer


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
