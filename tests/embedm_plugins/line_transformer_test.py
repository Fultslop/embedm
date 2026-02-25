from embedm_plugins.file.line_transformer import LineParams, LineTransformer

_CONTENT = "a\nb\nc\nd\ne\n"


def _run(content: str, line_range: str) -> str | None:
    return LineTransformer().execute(LineParams(content=content, line_range=line_range))


def test_single_line():
    assert _run(_CONTENT, "2") == "b"


def test_range():
    assert _run(_CONTENT, "2..4") == "b\nc\nd"


def test_open_end():
    result = _run(_CONTENT, "4..")
    assert result is not None
    assert result.startswith("d")


def test_open_start():
    assert _run(_CONTENT, "..3") == "a\nb\nc"


def test_out_of_bounds_returns_none():
    assert _run(_CONTENT, "99") is None


def test_invalid_format_returns_none():
    assert _run(_CONTENT, "1-5") is None
    assert _run(_CONTENT, "abc") is None


def test_start_greater_than_end_returns_none():
    assert _run(_CONTENT, "4..2") is None
