FEATURE: Synopsis plugin
========================================
Release v1.0
Created: 20/02/2026
Closed: `<date>`
Created by: FS

## Description

Create a plugin that generates a deterministic synopsis of the current document or the document referred to in the `source` option of the corresponding `Directive`.

Directive definition:

```yaml embedm
type: synopsis
source: optional — if omitted, summarise the current document (post-embed); otherwise summarise the referenced file
max_sentences: maximum number of sentences in the synopsis
algorithm: frequency | luhn
language: en | nl
sections: optional integer — number of leading blocks to use as input (default: all)
```

### Behaviour

- Executes **after** the `file` pass (so embedded content is resolved) and **before** the `toc` pass.
- Input text is cleaned before scoring (see below), then split into **blocks** and **sentences**.
- Output is rendered as a **blockquote**.
- Results are deterministic: ties in sentence scoring are broken by original sentence index.

### Text cleaning (applied before scoring)

The following are stripped from the input before any scoring takes place:

- Fenced code blocks (` ``` ... ``` `)
- Table rows (Markdown pipe syntax `|`)
- Blockquote markers (`> `)
- Heading markers (`#`, `##`, etc.)
- Bold / italic markers (`*`, `_`)
- Link and image syntax — link text is kept, URL and alt text are discarded
- List item markers (`-`, `*`, `+`, `1.`)

### Block model (unified for prose and markdown)

After cleaning, the text is split into **blocks** on blank lines (`\n\n`). Blank lines are the universal block separator in both formats:

- `.txt` / prose → each paragraph is a block
- `.md` → the intro paragraph and each section body are blocks (section headings become short fragments and are filtered by the minimum sentence length)

Sentence scoring uses a **positional decay weight** applied at the block level:

```
block_weight = 1.0 / (1 + block_index)
final_score  = algorithm_score × block_weight
```

Block 0 (intro / first paragraph) scores at full weight. Later blocks decay geometrically, so earlier content is preferred when scores are otherwise comparable. This reliably surfaces introductory material in both well-structured prose and markdown reference docs.

The `sections` option caps the input to the first N blocks, discarding the rest before scoring. This is the explicit variant of the same block model: use it when you know exactly which part of the document to summarise.

### Algorithms (both implemented in v1)

**Frequency:**
1. Tokenise into words; lowercase; strip punctuation.
2. Count word frequencies; filter a stopword list.
3. Score each sentence = sum of significant word frequencies, normalised by sentence length.

**Luhn:**
Same frequency/stopword pass, then for each sentence find "significant word clusters" — runs of words within a sliding window that contain at least one significant word. Score = (significant words in best cluster)² / total words in cluster. Rewards dense information rather than raw frequency.

Both algorithms multiply their sentence score by the block weight before ranking.

### Language support

Stopword lists are configurable per language. v1 ships with:
- `en` — English
- `nl` — Dutch

### Architecture

- Works like `toc_plugin`: reads `parent_document` string fragments at transform time; `Directive` objects are naturally skipped.
- Sourceless directives (no `source`) are leaf nodes — no planner changes needed.
- Plugin sequence: `file → table → hello_world_plugin → synopsis → toc`.

## Acceptance criteria

- The plugin generates a human-readable synopsis that correctly captures the source or current document.
- Both `frequency` and `luhn` algorithms are implemented and selectable via the directive.
- Stopword lists for `en` and `nl` are included and language is selectable via the directive.
- Code blocks, tables, blockquotes, and embedm directive blocks are excluded from scoring input.
- Block-level positional decay is applied: earlier blocks score higher.
- The `sections` option limits scoring input to the first N blocks.
- Output is rendered as a blockquote.
- The plugin is part of the standard plugins (alongside `file`, `table`, `toc`, etc.).
- Unit and integration tests are included.
- Regression tests are included.
- Documentation is out of scope for now.

## Comments

**20/02/2026 ML:**
Possible options
Tool/Library,Language,Algorithm,Complexity
Sumy,Python,"Multiple (Luhn, TextRank)","Low - ""Plug and play"""
NLTK / SpaCy,Python,Custom Frequency,Low - Great for DIY
Gensim,Python,TextRank (Optimized),Medium - Very fast
Apache OpenNLP,Java,MaxEnt / Statistical,Medium - Enterprise grade


**21/02/2026** Claude:

The algorithms, library-free

Of the four options, two are practical without a library:

Frequency (simplest):

Tokenise into words, lowercase, remove punctuation.
Count word frequencies; ignore a hardcoded stopword list (~150 common English words).
Score each sentence = sum of frequencies of its significant words, normalised by sentence length.
Return top-N sentences in original document order. ~80 lines of Python, fully deterministic, easy to test.
Luhn (slightly more nuanced):

Same frequency/stopword pass.
For each sentence, find "significant word clusters" — runs of words that include at least one significant word within a sliding window.
Score = (count of significant words in best cluster)² / total words in cluster. The cluster approach rewards sentences where important words are dense, not just frequent. ~120 lines, also deterministic.
TextRank — feasible but heavier. Requires a sentence-similarity matrix (word overlap or TF-IDF cosine) and a PageRank iteration loop. ~200 lines, still no library, but the convergence loop and tie-breaking need careful handling to stay deterministic. Probably too much for v1.

MaxEnt/Statistical — requires training data and an ML model. Out of scope without a library.

Recommendation: implement Frequency and Luhn for v1. They cover the "simple vs. cluster-aware" trade-off, share the same tokenisation pipeline, and are both ~10-15 minutes to test manually.

**21/02/2026** FS:

1. it should be post embed, and run before ToC to avoid including the Toc in the algorithm/word count. Maybe skip ```yaml embedm blocks ?
2. max_sentences
3. They usually serve as examples, so I'd say yes exclude themm
4. Good point. Let's include two languages English and  Dutch to demonstrate configurability UNLESS that blows up the scope beyond reason.

**21/02/2026** Claude + FS:

Block model added. Blank lines (`\n\n`) are the universal block separator for both `.txt` prose (paragraphs) and `.md` reference docs (section bodies). Positional decay weights earlier blocks higher — this reliably surfaces introductory material in both formats without format detection. The `sections` option is the explicit variant: cap input to first N blocks.
