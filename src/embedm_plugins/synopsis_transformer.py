from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from embedm.plugins.transformer_base import TransformerBase
from embedm_plugins.synopsis_resources import str_resources
from embedm_plugins.synopsis_stopwords import STOPWORDS
from embedm_plugins.text_processing import (
    _apply_block_weights,
    _build_word_freq,
    _clean_text,
    _flatten_blocks,
    _score_frequency,
    _select_top,
    _split_into_blocks,
    _tokenize,
)

_LUHN_WINDOW = 5


@dataclass
class SynopsisParams:
    text: str
    max_sentences: int
    algorithm: str
    language: str
    sections: int = field(default=0)


class SynopsisTransformer(TransformerBase[SynopsisParams]):
    params_type = SynopsisParams

    def execute(self, params: SynopsisParams) -> str:
        """Generate a blockquote synopsis by scoring and selecting top sentences."""
        assert params.text is not None, "text is required"
        assert params.max_sentences >= 1, "max_sentences must be >= 1"
        assert params.sections >= 0, "sections must be >= 0"

        text = _clean_text(params.text)
        blocks = _split_into_blocks(text, params.sections)
        if not blocks:
            return f"{str_resources.note_no_synopsis_content}\n"

        sentences, block_indices = _flatten_blocks(blocks)
        stopwords = STOPWORDS.get(params.language, STOPWORDS["en"])
        return f"> {_summarize(sentences, block_indices, params.algorithm, stopwords, params.max_sentences)}\n"


def _summarize(
    sentences: list[str],
    block_indices: list[int],
    algorithm: str,
    stopwords: frozenset[str],
    max_sentences: int,
) -> str:
    """Score, weight, select, and join sentences into a synopsis string."""
    scorer = _score_luhn if algorithm == "luhn" else _score_frequency
    raw_scores = scorer(sentences, stopwords)
    weighted = _apply_block_weights(raw_scores, block_indices)
    selected = _select_top(weighted, max_sentences)
    return " ".join(sentences[i] for i in selected)


def _score_luhn(sentences: list[str], stopwords: frozenset[str]) -> list[tuple[float, int]]:
    """Score sentences using Luhn's significant-word cluster algorithm."""
    tokenized = [_tokenize(s) for s in sentences]
    sig_words = _significant_words(_build_word_freq(tokenized, stopwords))
    if not sig_words:
        return [(0.0, i) for i in range(len(sentences))]
    return [(_best_cluster_score(_is_significant_mask(words, sig_words)), i) for i, words in enumerate(tokenized)]


def _is_significant_mask(words: list[str], sig_words: frozenset[str]) -> list[bool]:
    """Return a boolean mask indicating which words are significant."""
    return [w in sig_words for w in words]


def _best_cluster_score(is_sig: list[bool]) -> float:
    """Find the highest-scoring significant-word cluster in a sentence."""
    sig_positions = [i for i, s in enumerate(is_sig) if s]
    if not sig_positions:
        return 0.0
    return max(_score_cluster(sig_positions, start) for start in range(len(sig_positions)))


def _significant_words(word_freq: Counter[str]) -> frozenset[str]:
    """Return words with above-average frequency; empty if no significant words exist."""
    if not word_freq:
        return frozenset()
    avg_freq = sum(word_freq.values()) / len(word_freq)
    return frozenset(w for w, f in word_freq.items() if f > avg_freq)


def _score_cluster(sig_positions: list[int], start: int) -> float:
    """Score the cluster of significant words extending rightward from sig_positions[start]."""
    end = start
    while end + 1 < len(sig_positions) and sig_positions[end + 1] - sig_positions[end] - 1 <= _LUHN_WINDOW:
        end += 1
    sig_count = end - start + 1
    cluster_len = sig_positions[end] - sig_positions[start] + 1
    return (sig_count**2) / cluster_len
