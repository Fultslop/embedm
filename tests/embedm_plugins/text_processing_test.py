"""Regression tests for text_processing._clean_text."""

from embedm_plugins.synopsis.text_processing import clean_text


# ---------------------------------------------------------------------------
# snake_case identifier preservation (bug regression)
# ---------------------------------------------------------------------------


def test_clean_text_preserves_snake_case_identifier() -> None:
    result = clean_text("Refactor plugin_resources.py into file_resources.")
    assert "plugin_resources" in result
    assert "file_resources" in result


def test_clean_text_preserves_multiword_snake_case_on_same_line() -> None:
    # Root cause: non-greedy .*? matched _resources.py ... file_ as an italic span
    text = "split monolithic plugin_resources.py into file_resources and query_path_resources"
    result = clean_text(text)
    assert "plugin_resources" in result
    assert "file_resources" in result
    assert "query_path_resources" in result


def test_clean_text_preserves_upper_snake_case_constant() -> None:
    result = clean_text("Registered in DEFAULT_PLUGIN_SEQUENCE after synopsis.")
    assert "DEFAULT_PLUGIN_SEQUENCE" in result


# ---------------------------------------------------------------------------
# Markdown italic / bold removal still works
# ---------------------------------------------------------------------------


def test_clean_text_removes_single_underscore_italic() -> None:
    result = clean_text("This is _italic_ text.")
    assert "_italic_" not in result
    assert "italic" in result


def test_clean_text_removes_double_underscore_bold() -> None:
    result = clean_text("This is __bold__ text.")
    assert "__bold__" not in result
    assert "bold" in result


def test_clean_text_removes_triple_underscore_bold_italic() -> None:
    result = clean_text("This is ___bold italic___ text.")
    assert "___" not in result
    assert "bold italic" in result


def test_clean_text_removes_italic_adjacent_to_punctuation() -> None:
    result = clean_text("Use _emphasis_ here, and _more_ there.")
    assert "_emphasis_" not in result
    assert "_more_" not in result
    assert "emphasis" in result
    assert "more" in result
