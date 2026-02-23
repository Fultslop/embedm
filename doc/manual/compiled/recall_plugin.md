# Recall Plugin

version 0.6.1

The recall plugin retrieves the sentences from a document that are most relevant to a query. While the synopsis plugin summarises what a document is about, recall answers a specific question: *"which part of this document speaks to X?"*

This distinction matters most when a document is used as a knowledge source rather than read linearly — a reference manual, a technical spec, a meeting transcript, or a knowledge-base article. Embedding the whole document wastes context on irrelevant material; recall embeds only the passages that matter for the current question.

For an LLM like Claude this is particularly valuable. When a markdown document is assembled with embedm before being sent as context, a recall directive replaces a multi-page reference with the three or four sentences most relevant to what the reader (or the model) actually needs to know. The signal-to-noise ratio of the assembled context improves directly. This is offline retrieval-augmented generation — no vector database, no external service, no network dependency — just a static keyword query evaluated at compile time.

  - [Basic Usage](#basic-usage)
  - [The Query](#the-query)
  - [Recall vs Synopsis](#recall-vs-synopsis)
  - [Focusing with sections](#focusing-with-sections)
  - [Language](#language)
  - [Fallback behaviour](#fallback-behaviour)
  - [Block model and positional decay](#block-model-and-positional-decay)

## Basic Usage

Recall an external file by specifying `type: recall`, a `source` path, a `query`, and the maximum number of sentences to return. The plugin cleans the text (stripping code blocks, tables, and markdown formatting) before scoring. Output is always a blockquote.

```yaml
type: recall
source: ./synopsis_plugin.md
query: "how are sentences scored"
max_sentences: 2
```

> It scores sentences using statistical algorithms and selects the most representative ones, biased toward introductory content through a block-level positional decay model. The `algorithm` option controls how sentences are scored.

Omit `source` to query the document currently being processed — useful when the document itself is the knowledge base being assembled for downstream use.

```yaml
type: recall
query: "what is the block model"
max_sentences: 2
```

## The Query

The query is a plain-English phrase or question. The plugin tokenises it, removes stopwords, and scores every sentence in the source by the fraction of query tokens it contains:

```
overlap_score = |sentence_tokens ∩ query_tokens| / |query_tokens|
```

More specific queries produce sharper recall. A query like `"block weighting positional decay"` gives a tighter result than `"how does it work"` because specific technical terms rarely appear in unrelated sentences.

Query against the synopsis manual to find content about its positional model:

```yaml
type: recall
source: ./synopsis_plugin.md
query: "block positional decay weight"
max_sentences: 2
```

> It scores sentences using statistical algorithms and selects the most representative ones, biased toward introductory content through a block-level positional decay model. Block model and positional decay

## Recall vs Synopsis

Both plugins output a blockquote from the same source. The difference is in what drives sentence selection. Synopsis picks the sentences that best represent the whole document — the most statistically central content. Recall picks the sentences most relevant to a specific question, regardless of how representative they are overall.

Here is the same source processed by each:

**Synopsis** — most representative sentences from the table plugin manual:

```yaml
type: synopsis
source: ./table_plugin.md
max_sentences: 2
algorithm: frequency
```

> The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown.

**Recall** — sentences from the same source about filtering:

```yaml
type: recall
source: ./table_plugin.md
query: "filter rows conditions operators"
max_sentences: 2
```

> Use `filter` to keep only rows that match a set of conditions. Multiple conditions are ANDed together.

Synopsis pulls introductory, general-purpose content. Recall pulls the specific section answering the question. Neither is better in the abstract — they serve different assembly goals.

## Focusing with sections

Long documents often contain more material than is relevant to any one question. `sections` caps the scoring input to the first N blank-line-separated blocks, limiting retrieval to the introductory portion of a document.

Without `sections`, recall considers the full document:

```yaml
type: recall
source: ./table_plugin.md
query: "column selection rename alias"
max_sentences: 2
```

> It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown. Column order follows the order in the `select` expression.

With `sections: 2`, only the first two blocks are considered:

```yaml
type: recall
source: ./table_plugin.md
query: "column selection rename alias"
max_sentences: 2
sections: 2
```

> The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown.

> **Note:** `sections: 0` (the default) means all blocks are included.

## Language

Use `language` to select the appropriate stopword list. Stopwords (articles, prepositions, common verbs) are excluded from both query tokenisation and sentence scoring so they do not distort overlap calculations.

Supported values: `en` (default), `nl`.

```yaml
type: recall
source: ./synopsis_plugin.md
query: "sentence scoring algorithm"
max_sentences: 2
language: en
```

## Fallback behaviour

When no sentence contains any of the query tokens — for example, a highly specific technical query against a document that never uses that vocabulary — recall falls back to frequency scoring and prepends a note to the output:

> [!NOTE]
> No sentences matched the query. Showing most representative sentences instead.

This guarantees that the directive always produces useful output, never a blank blockquote. The fallback uses the same frequency algorithm as the synopsis plugin.

## Block model and positional decay

Recall shares the same block model as the synopsis plugin. Blank lines divide the source document into blocks. Earlier blocks receive higher weight:

```
block_weight = 1.0 / (1 + block_index)
final_score  = overlap_score × block_weight
```

When two sentences have equal query overlap, the one appearing earlier in the document wins. This reflects the common pattern where important definitions and summaries appear at the start of a section.
