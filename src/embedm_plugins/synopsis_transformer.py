from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from embedm.plugins.transformer_base import TransformerBase
from embedm_plugins.plugin_resources import str_resources
from embedm_plugins.synopsis_stopwords import STOPWORDS

_LUHN_WINDOW = 5
_MIN_SENTENCE_WORDS = 3


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

        sentences: list[str] = []
        block_indices: list[int] = []
        for block_idx, block_sentences in enumerate(blocks):
            sentences.extend(block_sentences)
            block_indices.extend([block_idx] * len(block_sentences))

        stopwords = STOPWORDS.get(params.language, STOPWORDS["en"])
        scorer = _score_luhn if params.algorithm == "luhn" else _score_frequency
        raw_scores = scorer(sentences, stopwords)
        weighted = [(score * (1.0 / (1 + block_indices[i])), i) for score, i in raw_scores]
        selected = _select_top(weighted, params.max_sentences)

        result = " ".join(sentences[i] for i in selected)
        return f"> {result}\n"


def _clean_text(text: str) -> str:
    """Strip markdown syntax unsuitable for summarisation: code blocks, tables, formatting."""
    # Remove fenced code blocks (``` ... ```)
    text = re.sub(r"```+.*?```+", "", text, flags=re.DOTALL)
    # Remove table rows (lines starting with |)
    lines = [line for line in text.splitlines() if not line.strip().startswith("|")]
    text = "\n".join(lines)
    # Remove blockquote markers
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # Remove heading markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold / italic markers
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", text)
    # Remove links and images: [text](url) → text, ![alt](url) → remove
    text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove list markers
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # Collapse horizontal whitespace only — preserve newlines as sentence boundaries
    return re.sub(r"[ \t]+", " ", text).strip()


def _split_into_blocks(text: str, max_blocks: int) -> list[list[str]]:
    """Split cleaned text on blank lines into blocks; return per-block sentence lists."""
    raw_blocks = re.split(r"\n{2,}", text)
    capped = raw_blocks[:max_blocks] if max_blocks > 0 else raw_blocks
    return [sentences for block in capped if (sentences := _block_to_sentences(block))]


def _block_to_sentences(text: str) -> list[str]:
    """Split a block on punctuation boundaries and newlines, filtering short fragments."""
    raw = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip() for s in raw if len(_tokenize(s)) >= _MIN_SENTENCE_WORDS]


def _tokenize(text: str) -> list[str]:
    """Return lowercase ASCII word tokens."""
    return re.findall(r"\b[a-z]+\b", text.lower())


def _score_frequency(sentences: list[str], stopwords: frozenset[str]) -> list[tuple[float, int]]:
    """Score sentences by sum of significant word frequencies, normalised by sentence length."""
    tokenized = [_tokenize(s) for s in sentences]
    word_freq = _build_word_freq(tokenized, stopwords)
    return [(_sentence_score(words, word_freq, stopwords), i) for i, words in enumerate(tokenized)]


def _score_luhn(sentences: list[str], stopwords: frozenset[str]) -> list[tuple[float, int]]:
    """Score sentences using Luhn's significant-word cluster algorithm."""
    tokenized = [_tokenize(s) for s in sentences]
    sig_words = _significant_words(_build_word_freq(tokenized, stopwords))
    if not sig_words:
        return [(0.0, i) for i in range(len(sentences))]
    return [(_best_cluster_score([w in sig_words for w in words]), i) for i, words in enumerate(tokenized)]


def _best_cluster_score(is_sig: list[bool]) -> float:
    """Find the highest-scoring significant-word cluster in a sentence."""
    sig_positions = [i for i, s in enumerate(is_sig) if s]
    if not sig_positions:
        return 0.0
    return max(_score_cluster(sig_positions, start) for start in range(len(sig_positions)))


def _select_top(scores: list[tuple[float, int]], max_sentences: int) -> list[int]:
    """Return up to max_sentences indices in original document order, ranked by score."""
    ranked = sorted(scores, key=lambda x: (-x[0], x[1]))
    top = sorted(i for _, i in ranked[:max_sentences])
    return top


def _build_word_freq(tokenized: list[list[str]], stopwords: frozenset[str]) -> Counter[str]:
    """Count significant word frequencies across all sentence tokens."""
    word_freq: Counter[str] = Counter()
    for words in tokenized:
        word_freq.update(w for w in words if w not in stopwords)
    return word_freq


def _sentence_score(words: list[str], word_freq: Counter[str], stopwords: frozenset[str]) -> float:
    """Score a single sentence by normalised significant word frequency."""
    if not words:
        return 0.0
    return sum(word_freq[w] for w in words if w not in stopwords) / len(words)


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
