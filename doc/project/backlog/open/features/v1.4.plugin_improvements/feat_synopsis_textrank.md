FEATURE: Synopsis — TextRank algorithm
========================================
Draft
Created: 21/02/2026
Closed: `<date>`
Created by: FS

## Description

Add `algorithm: textrank` to the synopsis plugin.

TextRank is a graph-based ranking algorithm. Each sentence is a node; edges are weighted by the word-overlap similarity between sentence pairs. A PageRank-style iteration then identifies the sentences that are most "central" to the document — sentences that echo the vocabulary of many other sentences score higher.

This differs from the current frequency approach in a meaningful way: frequency rewards sentences containing globally common words; TextRank rewards sentences whose vocabulary is representative of the document as a whole. In practice this leads to better coverage and fewer artifacts caused by high-frequency but low-content words (e.g. section header terms that repeat throughout a reference document).

**Algorithm sketch (no external dependencies required):**

1. Tokenise all sentences; compute pairwise overlap scores:
   `overlap(i, j) = |tokens_i ∩ tokens_j| / (log|tokens_i| + log|tokens_j|)`
2. Build a similarity matrix (N × N for N sentences).
3. Normalise each row so it sums to 1 (stochastic matrix).
4. Iterate: `score[i] = (1 - d) + d × Σ_j score[j] × sim[j][i]` where `d ≈ 0.85`.
5. Run until convergence (delta < 1e-4) or a fixed iteration cap (e.g. 100).
6. Multiply final scores by block positional weight (existing block model applies).

The block model and `sections` option compose with TextRank unchanged — they govern which sentences enter the graph, not the ranking logic.

Determinism is guaranteed by:
- Initialising all scores to `1.0 / N`
- Tie-breaking on original sentence index (same as current `_select_top`)

## Acceptance criteria

- `algorithm: textrank` is a valid value; validated and documented alongside `frequency` and `luhn`
- The algorithm produces deterministic output across multiple runs on the same input
- Block positional decay applies to TextRank scores the same way it applies to frequency and Luhn
- Unit tests cover: similarity matrix construction, convergence, score ordering, tie-breaking
- Regression example added

## Comments

`21/02/2026 FS/Claude:` Identified during synopsis quality review. TextRank does not require stopwords (similarity is self-normalising), though excluding them from the similarity computation would likely improve results. Consider making stopword filtering in TextRank optional or always-on and document the choice.
