from __future__ import annotations

import re
from collections import Counter

_MIN_SENTENCE_WORDS = 3


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
    text = re.sub(r"(?<!\w)_{1,3}(.*?)_{1,3}(?!\w)", r"\1", text)
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


def _apply_block_weights(raw_scores: list[tuple[float, int]], block_indices: list[int]) -> list[tuple[float, int]]:
    """Apply positional block decay: earlier blocks score higher for equal overlap."""
    return [(score * (1.0 / (1 + block_indices[i])), i) for score, i in raw_scores]


def _flatten_blocks(blocks: list[list[str]]) -> tuple[list[str], list[int]]:
    """Flatten block-of-sentences into a flat sentence list with a parallel block-index list."""
    sentences: list[str] = []
    block_indices: list[int] = []
    for block_idx, block_sentences in enumerate(blocks):
        sentences.extend(block_sentences)
        block_indices.extend([block_idx] * len(block_sentences))
    return sentences, block_indices


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
