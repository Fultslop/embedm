"""Unit tests for RecallTransformer and _score_recall."""

import pytest

from embedm_plugins.recall_transformer import (
    RecallParams,
    RecallTransformer,
    _score_recall,
    _score_with_fallback,
)
from embedm_plugins.text_processing import _flatten_blocks


def _run(text: str, query: str, max_sentences: int = 3, language: str = "en", sections: int = 0) -> str:
    return RecallTransformer().execute(RecallParams(text, query, max_sentences, language, sections))


# ---------------------------------------------------------------------------
# _score_recall
# ---------------------------------------------------------------------------


def test_score_recall_empty_query_tokens_returns_all_zeros() -> None:
    scores = _score_recall(["hello world", "foo bar baz"], frozenset())
    assert all(s == 0.0 for s, _ in scores)
    assert [i for _, i in scores] == [0, 1]


def test_score_recall_full_overlap_gives_score_one() -> None:
    # sentence contains all query tokens
    scores = _score_recall(["authentication session management"], frozenset({"authentication", "session"}))
    assert scores[0][0] == pytest.approx(1.0)


def test_score_recall_partial_overlap() -> None:
    scores = _score_recall(["authentication only here"], frozenset({"authentication", "session"}))
    assert scores[0][0] == pytest.approx(0.5)


def test_score_recall_no_overlap_gives_zero() -> None:
    scores = _score_recall(["completely unrelated words"], frozenset({"authentication", "session"}))
    assert scores[0][0] == 0.0


def test_score_recall_preserves_sentence_indices() -> None:
    sentences = ["first sentence here", "second sentence here", "third sentence here"]
    scores = _score_recall(sentences, frozenset({"second"}))
    indices = [i for _, i in scores]
    assert indices == [0, 1, 2]
    # only index 1 has overlap
    match_scores = {i: s for s, i in scores}
    assert match_scores[1] > 0.0
    assert match_scores[0] == 0.0
    assert match_scores[2] == 0.0


# ---------------------------------------------------------------------------
# RecallTransformer.execute — happy path
# ---------------------------------------------------------------------------


def test_execute_returns_blockquote_for_matching_query() -> None:
    text = (
        "Authentication handles user login and session management.\n\n"
        "The database stores user credentials securely.\n\n"
        "Caching improves response times for repeated requests."
    )
    result = _run(text, "authentication session", max_sentences=1)
    assert result.startswith("> ")
    assert result.endswith("\n")
    assert "Authentication" in result or "session" in result.lower()


def test_execute_top_sentence_has_highest_query_overlap() -> None:
    text = (
        "Authentication and session management are critical security concerns.\n\n"
        "The weather today is sunny and warm.\n\n"
        "Proper logging helps with debugging complex systems."
    )
    result = _run(text, "authentication session security", max_sentences=1)
    assert "Authentication" in result or "session" in result.lower()


def test_execute_respects_max_sentences() -> None:
    text = "\n\n".join(
        [
            "Authentication handles session management for users properly.",
            "Session tokens expire after a configured timeout period.",
            "Login authentication requires valid user credentials here.",
            "Caching improves performance for repeated read operations.",
        ]
    )
    result = _run(text, "authentication session", max_sentences=2)
    # blockquote content is a single joined string — count sentences by splitting on ". "
    content = result.lstrip("> ").rstrip("\n")
    assert content.count(".") <= 2


# ---------------------------------------------------------------------------
# RecallTransformer.execute — fallback
# ---------------------------------------------------------------------------


def test_execute_fallback_when_no_overlap_includes_note() -> None:
    text = (
        "The quick brown fox jumps over the lazy dog.\n\n"
        "Space exploration advances human understanding of the cosmos.\n\n"
        "Renewable energy reduces dependence on fossil fuels."
    )
    result = _run(text, "zxqwerty unmatched token", max_sentences=1)
    assert "[!NOTE]" in result
    assert "No sentences matched" in result
    # should still contain a blockquote result
    assert "> " in result


def test_execute_fallback_still_returns_blockquote_content() -> None:
    text = (
        "Space exploration is a fascinating human endeavour.\n\n"
        "Cooking is an art that combines flavour and technique.\n\n"
        "Mountains offer breathtaking views for hikers."
    )
    result = _run(text, "zzznomatchzzz", max_sentences=1)
    lines = result.splitlines()
    # at least one line should start with "> " but not be a note
    blockquote_lines = [ln for ln in lines if ln.startswith("> ") and "[!" not in ln]
    assert blockquote_lines


# ---------------------------------------------------------------------------
# RecallTransformer.execute — edge cases
# ---------------------------------------------------------------------------


def test_execute_empty_content_returns_note() -> None:
    result = _run("", "any query", max_sentences=1)
    assert "[!NOTE]" in result
    assert "No relevant content" in result


def test_execute_block_positional_decay_prefers_earlier_blocks() -> None:
    # Both blocks have the same overlap score; earlier block should win
    text = (
        "Authentication session management block one appears first.\n\n"
        "Authentication session management block two appears second."
    )
    result = _run(text, "authentication session", max_sentences=1)
    assert "one" in result.lower()


def test_execute_sections_caps_input() -> None:
    text = (
        "Completely irrelevant content about cooking recipes.\n\n"
        "Authentication and session management are handled here."
    )
    # With sections=1, only the first block is considered
    result = _run(text, "authentication session", max_sentences=1, sections=1)
    # Should not find the auth content (it's in block 2), triggering fallback
    assert "[!NOTE]" in result
