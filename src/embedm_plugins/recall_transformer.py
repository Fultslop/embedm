from __future__ import annotations

from dataclasses import dataclass, field

from embedm.plugins.transformer_base import TransformerBase
from embedm_plugins.recall_resources import str_resources
from embedm_plugins.synopsis_stopwords import STOPWORDS
from embedm_plugins.text_processing import (
    _apply_block_weights,
    _clean_text,
    _flatten_blocks,
    _score_frequency,
    _select_top,
    _split_into_blocks,
    _tokenize,
)


@dataclass
class RecallParams:
    text: str
    query: str
    max_sentences: int
    language: str
    sections: int = field(default=0)


class RecallTransformer(TransformerBase[RecallParams]):
    """Retrieve the most relevant sentences for a query using sparse token-overlap scoring."""

    params_type = RecallParams

    def execute(self, params: RecallParams) -> str:
        """Select top sentences by query token overlap and return them as a GFM blockquote."""
        assert params.text is not None, "text is required"
        assert params.query is not None, "query is required"
        assert params.max_sentences >= 1, "max_sentences must be >= 1"
        assert params.sections >= 0, "sections must be >= 0"

        text = _clean_text(params.text)
        blocks = _split_into_blocks(text, params.sections)
        if not blocks:
            return f"{str_resources.note_no_recall_content}\n"

        sentences, block_indices = _flatten_blocks(blocks)
        stopwords = STOPWORDS.get(params.language, STOPWORDS["en"])
        query_tokens = frozenset(_tokenize(params.query)) - stopwords

        raw_scores, fallback = _score_with_fallback(sentences, query_tokens, stopwords)
        weighted = _apply_block_weights(raw_scores, block_indices)
        selected = _select_top(weighted, params.max_sentences)

        result = " ".join(sentences[i] for i in selected)
        note = f"{str_resources.note_recall_fallback}\n\n" if fallback else ""
        return f"{note}> {result}\n"


def _score_with_fallback(
    sentences: list[str],
    query_tokens: frozenset[str],
    stopwords: frozenset[str],
) -> tuple[list[tuple[float, int]], bool]:
    """Score sentences by query overlap; fall back to frequency scoring when no overlap exists."""
    raw_scores = _score_recall(sentences, query_tokens)
    fallback = all(score == 0.0 for score, _ in raw_scores)
    if fallback:
        raw_scores = _score_frequency(sentences, stopwords)
    return raw_scores, fallback


def _score_recall(sentences: list[str], query_tokens: frozenset[str]) -> list[tuple[float, int]]:
    """Score each sentence by the fraction of query tokens it contains."""
    if not query_tokens:
        return [(0.0, i) for i in range(len(sentences))]
    scores: list[tuple[float, int]] = []
    for i, sentence in enumerate(sentences):
        tokens = set(_tokenize(sentence))
        overlap = len(tokens & query_tokens) / len(query_tokens)
        scores.append((overlap, i))
    return scores
