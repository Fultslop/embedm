"""Unit tests for SynopsisTransformer and its helper functions."""

import pytest

from embedm_plugins.synopsis_transformer import (
    SynopsisParams,
    SynopsisTransformer,
    _best_cluster_score,
    _block_to_sentences,
    _clean_text,
    _score_frequency,
    _score_luhn,
    _select_top,
    _split_into_blocks,
    _tokenize,
)

# ---------------------------------------------------------------------------
# _tokenize
# ---------------------------------------------------------------------------


def test_tokenize_lowercases_and_extracts_words() -> None:
    assert _tokenize("Hello World!") == ["hello", "world"]


def test_tokenize_strips_punctuation() -> None:
    assert _tokenize("end.") == ["end"]


def test_tokenize_empty() -> None:
    assert _tokenize("") == []


# ---------------------------------------------------------------------------
# _clean_text
# ---------------------------------------------------------------------------


def test_clean_text_removes_fenced_code_block() -> None:
    text = "Intro sentence with enough words here.\n\n```python\ncode = True\n```\n\nOutro sentence with enough words."
    result = _clean_text(text)
    assert "code" not in result
    assert "Intro" in result
    assert "Outro" in result


def test_clean_text_removes_table_rows() -> None:
    text = "Before the table with words.\n| A | B |\n|---|---|\n| 1 | 2 |\nAfter the table with words."
    result = _clean_text(text)
    assert "|" not in result
    assert "Before" in result
    assert "After" in result


def test_clean_text_removes_heading_markers() -> None:
    result = _clean_text("## My Section\n\nSome prose follows.")
    assert "##" not in result
    assert "My Section" in result


def test_clean_text_removes_bold_markers() -> None:
    result = _clean_text("This is **important** text.")
    assert "**" not in result
    assert "important" in result


def test_clean_text_removes_links() -> None:
    result = _clean_text("Read [the docs](https://example.com) for details.")
    assert "https" not in result
    assert "the docs" in result


def test_clean_text_normalises_horizontal_whitespace() -> None:
    result = _clean_text("   lots   of   spaces   ")
    assert "  " not in result


def test_clean_text_preserves_newlines() -> None:
    # Newlines must survive so that headings/list items can be split and filtered
    result = _clean_text("First line.\nSecond line.\n")
    assert "\n" in result


def test_clean_text_removes_blockquote_markers() -> None:
    result = _clean_text("> This is a note inside a blockquote.")
    assert ">" not in result
    assert "note" in result


# ---------------------------------------------------------------------------
# _block_to_sentences
# ---------------------------------------------------------------------------


def test_block_to_sentences_splits_on_newlines() -> None:
    # Headings and list items land on their own lines after cleaning;
    # they must be treated as separate fragments (and filtered if too short)
    text = "Basic Usage\nSelecting Columns\nThe plugin embeds data as a formatted table with options."
    sentences = _block_to_sentences(text)
    # The two short headings are filtered (<3 words); only the prose sentence survives
    assert len(sentences) == 1
    assert "formatted" in sentences[0]


def test_block_to_sentences_basic() -> None:
    text = "The cat sat on the mat. The dog ran away quickly. The bird sang a song."
    sentences = _block_to_sentences(text)
    assert len(sentences) == 3


def test_block_to_sentences_filters_short_fragments() -> None:
    # "OK." and "Sure." are too short (< 3 words)
    text = "OK. This is a complete sentence with words. Sure."
    sentences = _block_to_sentences(text)
    assert len(sentences) == 1
    assert "complete" in sentences[0]


def test_block_to_sentences_empty() -> None:
    assert _block_to_sentences("") == []


# ---------------------------------------------------------------------------
# _split_into_blocks
# ---------------------------------------------------------------------------


def test_split_into_blocks_single_block() -> None:
    text = "First sentence with enough words. Second sentence with enough words."
    blocks = _split_into_blocks(text, 0)
    assert len(blocks) == 1


def test_split_into_blocks_multiple_blocks() -> None:
    text = "First sentence with enough words.\n\nSecond sentence with enough words."
    blocks = _split_into_blocks(text, 0)
    assert len(blocks) == 2


def test_split_into_blocks_max_blocks_caps_result() -> None:
    text = "Block one has a long sentence here.\n\nBlock two has a long sentence here.\n\nBlock three sentence here."
    blocks = _split_into_blocks(text, 2)
    assert len(blocks) == 2


def test_split_into_blocks_filters_blocks_with_no_sentences() -> None:
    # Trailing blank lines produce an empty block that gets filtered
    text = "Sentence one is long enough.\n\n\n\n"
    blocks = _split_into_blocks(text, 0)
    assert len(blocks) == 1


# ---------------------------------------------------------------------------
# _best_cluster_score
# ---------------------------------------------------------------------------


def test_best_cluster_score_no_significant_words() -> None:
    assert _best_cluster_score([False, False, False]) == 0.0


def test_best_cluster_score_empty() -> None:
    assert _best_cluster_score([]) == 0.0


def test_best_cluster_score_single_significant_word() -> None:
    assert _best_cluster_score([True, False, False]) == 1.0


def test_best_cluster_score_two_adjacent_significant_words() -> None:
    # cluster [T, T]: sig=2, len=2, score=4/2=2.0
    assert _best_cluster_score([True, True, False]) == 2.0


def test_best_cluster_score_two_significant_words_with_gap() -> None:
    # cluster [T, F, T]: sig=2, len=3, score=4/3
    result = _best_cluster_score([True, False, True])
    assert abs(result - 4 / 3) < 1e-9


def test_best_cluster_score_gap_beyond_window_splits_clusters() -> None:
    # gap of 6 between sig words exceeds LUHN_WINDOW=5 → two single-word clusters, score=1.0
    is_sig = [True] + [False] * 6 + [True]
    assert _best_cluster_score(is_sig) == 1.0


def test_best_cluster_score_gap_at_window_boundary() -> None:
    # gap of 5 is exactly LUHN_WINDOW — joint cluster score is 4/7 < 1.0,
    # so the single-word cluster at the end still wins with score 1.0
    is_sig = [True] + [False] * 5 + [True]
    result = _best_cluster_score(is_sig)
    assert result == 1.0


# ---------------------------------------------------------------------------
# _score_frequency
# ---------------------------------------------------------------------------

_EN_STOPWORDS: frozenset[str] = frozenset({"is", "a", "on", "the"})

# Sentences where "space" appears twice → higher frequency → higher score for sent 0 and 2
_FREQ_SENTENCES = [
    "Space exploration is fascinating.",       # score: (2+1+1)/4 = 1.0
    "Mars is a red planet.",                   # score: (1+1+1)/5 = 0.6
    "Astronauts explore space on missions.",   # score: (1+1+2+1)/5 = 1.0
]


def test_score_frequency_returns_correct_scores() -> None:
    scores = _score_frequency(_FREQ_SENTENCES, _EN_STOPWORDS)
    assert len(scores) == 3
    score_map = {i: s for s, i in scores}
    assert abs(score_map[0] - 1.0) < 1e-9
    assert abs(score_map[1] - 0.6) < 1e-9
    assert abs(score_map[2] - 1.0) < 1e-9


def test_score_frequency_all_stopwords_scores_zero() -> None:
    sentences = ["is a the on."]
    scores = _score_frequency(sentences, _EN_STOPWORDS)
    assert scores[0][0] == 0.0


# ---------------------------------------------------------------------------
# _score_luhn
# ---------------------------------------------------------------------------


def test_score_luhn_penalises_sentences_with_no_significant_words() -> None:
    # "space" appears twice → above-average → sig. sent2 has no "space" → score 0.0
    sentences = [
        "Space is everywhere.",
        "Mars is a planet.",
        "Astronauts explore space.",
    ]
    scores = _score_luhn(sentences, _EN_STOPWORDS)
    score_map = {i: s for s, i in scores}
    assert score_map[1] == 0.0  # no "space" → no significant words


def test_score_luhn_all_unique_words_scores_zero_for_all() -> None:
    # All word frequencies = 1, avg = 1; nothing > avg → no sig words → all 0
    sentences = ["Apple banana cherry date.", "Elephant fig grape honeydew.", "Iris jasmine kiwi lemon."]
    scores = _score_luhn(sentences, frozenset())
    for score, _ in scores:
        assert score == 0.0


# ---------------------------------------------------------------------------
# _select_top
# ---------------------------------------------------------------------------


def test_select_top_returns_in_original_order() -> None:
    scores = [(1.0, 0), (0.6, 1), (1.0, 2)]
    result = _select_top(scores, max_sentences=2)
    assert result == [0, 2]


def test_select_top_tie_breaks_by_original_index() -> None:
    scores = [(1.0, 0), (1.0, 1), (1.0, 2)]
    result = _select_top(scores, max_sentences=1)
    assert result == [0]


def test_select_top_respects_max_sentences() -> None:
    scores = [(1.0, 0), (0.9, 1), (0.8, 2)]
    result = _select_top(scores, max_sentences=2)
    assert result == [0, 1]


def test_select_top_max_larger_than_available() -> None:
    scores = [(1.0, 0), (0.5, 1)]
    result = _select_top(scores, max_sentences=5)
    assert result == [0, 1]


# ---------------------------------------------------------------------------
# SynopsisTransformer.execute — integration
# ---------------------------------------------------------------------------


_TRANSFORMER = SynopsisTransformer()


def test_execute_frequency_selects_top_two_in_document_order() -> None:
    # Traced: space(freq=2) → sent0 and sent2 both score 1.0; sent1 scores 0.6
    params = SynopsisParams(
        text="Space exploration is fascinating. Mars is a red planet. Astronauts explore space on missions.",
        max_sentences=2,
        algorithm="frequency",
        language="en",
    )
    result = _TRANSFORMER.execute(params)
    assert result == "> Space exploration is fascinating. Astronauts explore space on missions.\n"


def test_execute_frequency_max_sentences_one_picks_highest() -> None:
    params = SynopsisParams(
        text="Space exploration is fascinating. Mars is a red planet. Astronauts explore space on missions.",
        max_sentences=1,
        algorithm="frequency",
        language="en",
    )
    result = _TRANSFORMER.execute(params)
    # sent0 and sent2 tie at 1.0; tie broken by original index → sent0
    assert result == "> Space exploration is fascinating.\n"


def test_execute_luhn_selects_sentences_with_significant_clusters() -> None:
    params = SynopsisParams(
        text="Space exploration is fascinating. Mars is a red planet. Astronauts explore space on missions.",
        max_sentences=2,
        algorithm="luhn",
        language="en",
    )
    result = _TRANSFORMER.execute(params)
    # "space" is above average → sig. sent1 has no space → score 0.0; sent0 and sent2 score 1.0
    assert result == "> Space exploration is fascinating. Astronauts explore space on missions.\n"


def test_execute_strips_code_block_before_scoring() -> None:
    text = (
        "Whales are marine mammals with large brains.\n"
        "```python\ncode = True\n```\n"
        "Dolphins are also intelligent marine mammals."
    )
    params = SynopsisParams(text=text, max_sentences=2, algorithm="frequency", language="en")
    result = _TRANSFORMER.execute(params)
    assert "code" not in result
    assert result.startswith("> ")


def test_execute_returns_note_when_no_meaningful_sentences() -> None:
    params = SynopsisParams(text="", max_sentences=3, algorithm="frequency", language="en")
    result = _TRANSFORMER.execute(params)
    assert "[!NOTE]" in result


def test_execute_dutch_language() -> None:
    # Simple sanity check that nl language path runs without error
    params = SynopsisParams(
        text="De blauwe vinvis is het grootste dier op aarde. Vinvissen leven in de oceaan.",
        max_sentences=1,
        algorithm="frequency",
        language="nl",
    )
    result = _TRANSFORMER.execute(params)
    assert result.startswith("> ")


def test_execute_block_weighting_prefers_earlier_blocks() -> None:
    # Two identical sentences in separate blocks: block 0 gets weight 1.0, block 1 gets 0.5.
    # With max_sentences=1, the block 0 sentence must win.
    text = "The cat sat on the mat quickly.\n\nThe cat sat on the mat quickly."
    params = SynopsisParams(text=text, max_sentences=1, algorithm="frequency", language="en")
    result = _TRANSFORMER.execute(params)
    # Both raw scores equal; block 0 wins due to positional decay
    assert result == "> The cat sat on the mat quickly.\n"


def test_execute_sections_caps_input_blocks() -> None:
    # With sections=1, only the first block is considered.
    # Block 0: "The ocean is vast and deep."
    # Block 1: "Stars explode in supernovae producing heavy elements."
    # Without sections cap, block 1's unique words may outscore block 0 sentences.
    # With sections=1, only block 0 sentences are available.
    text = "The ocean is vast and deep.\n\nStars explode in supernovae producing heavy elements."
    params = SynopsisParams(text=text, max_sentences=1, algorithm="frequency", language="en", sections=1)
    result = _TRANSFORMER.execute(params)
    assert "ocean" in result
