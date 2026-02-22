FEATURE: Synopsis — MMR diversity re-ranking
========================================
Draft
Created: 21/02/2026
Closed: `<date>`
Created by: FS

## Description

Add a `diversity` option to the synopsis plugin that applies Maximal Marginal Relevance (MMR) re-ranking after the base algorithm scores sentences.

The current approach selects the top-N sentences by score, which can produce redundant output: two sentences that say nearly the same thing with different words both score highly and both get selected. MMR trades off relevance against redundancy by iteratively picking sentences that are both relevant to the document and dissimilar to sentences already selected.

**Algorithm:**

After base scoring (frequency, Luhn, or TextRank), apply MMR selection:

```
selected = []
candidates = all sentences with their scores

while len(selected) < max_sentences and candidates:
    best = argmax over c in candidates of:
        diversity × score(c) - (1 - diversity) × max_sim(c, selected)
    selected.append(best)
    candidates.remove(best)
```

`max_sim(c, selected)` is the cosine similarity (or Jaccard/word-overlap) between sentence `c` and the most similar already-selected sentence.

`diversity: 0.0` = pure relevance (identical to current behaviour).
`diversity: 1.0` = pure diversity (sentences as different from each other as possible).
`diversity: 0.5` = balanced (recommended default if enabled).

The block positional weight is applied to the base score before MMR selection runs — the relevance term already encodes positional preference.

**Directive option:**

```yaml
diversity: 0.5   # float in [0.0, 1.0], default: 0.0
```

## Acceptance criteria

- `diversity` option is validated as a float in [0.0, 1.0]
- `diversity: 0.0` produces identical output to the current implementation (no regression)
- Higher diversity values visibly reduce redundancy in the selected set
- MMR composes with all three algorithms and with the block model
- Unit tests cover: pure relevance, pure diversity, balanced, edge cases (single sentence, all identical sentences)

## Comments

`21/02/2026 FS/Claude:` Identified during synopsis quality review. The Moby Dick Luhn output showed 3 sentences with overlapping sea/water themes selected. MMR would have diversified the pick. This is an additive post-processing step — it does not change the scoring algorithms and can be shipped independently of TextRank.
