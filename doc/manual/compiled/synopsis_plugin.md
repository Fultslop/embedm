# Synopsis Plugin

version 1.0.0

The synopsis plugin generates a concise blockquote summary of a document. It scores sentences using statistical algorithms and selects the most representative ones, biased toward introductory content through a block-level positional decay model.

  - [Basic Usage](#basic-usage)
  - [Algorithms](#algorithms)
    - [Frequency](#frequency)
    - [Luhn](#luhn)
  - [Language](#language)
  - [Focusing with sections](#focusing-with-sections)
  - [Block model and positional decay](#block-model-and-positional-decay)

## Basic Usage

Summarize an external file by specifying `type: synopsis` and a `source` path. The plugin cleans the text (stripping code blocks, tables, and markdown formatting) before scoring. Output is always a blockquote.

```yaml
type: synopsis
source: ./table_plugin.md
max_sentences: 3
```

> The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown. Column order follows the order in the `select` expression.

Omit `source` to summarize the document currently being processed — useful at the top of a document to give readers an upfront overview. The synopsis runs after file embeds are resolved, so embedded content is included in the scoring input.

```yaml
type: synopsis
max_sentences: 2
```

## Algorithms

The `algorithm` option controls how sentences are scored. Both algorithms share the same tokenisation and stopword-filtering pipeline.

### Frequency

The default. Scores each sentence by the sum of its significant word frequencies, normalised by sentence length. Words that appear often across the whole document are considered significant. Reliable and fast — a good default for most documents.

```yaml
type: synopsis
source: ./table_plugin.md
max_sentences: 3
algorithm: frequency
```

> The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown. Column order follows the order in the `select` expression.

### Luhn

Scores sentences by their densest cluster of significant words, using a sliding window. A sentence where important words appear close together scores higher than one where the same words are spread out. Better at picking out specific claims or conclusions in technical writing.

```yaml
type: synopsis
source: ./table_plugin.md
max_sentences: 3
algorithm: luhn
```

> The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown. Without any other options the full dataset is rendered, so use `limit` on large files.

## Language

Use `language` to select the appropriate stopword list. Stopwords (articles, prepositions, common verbs) are excluded from scoring so they do not inflate sentence scores artificially.

Supported values: `en` (default), `nl`.

```yaml
type: synopsis
source: ./table_plugin.md
max_sentences: 3
language: en
```

## Focusing with sections

Long documents — especially reference manuals — often have a descriptive introduction followed by many dense detail sections. The block model already biases toward the beginning, but `sections` provides explicit control: it caps the scoring input to the first N blank-line-separated blocks.

Without `sections`, the algorithm considers the full document:

```yaml
type: synopsis
source: ./table_plugin.md
max_sentences: 3
algorithm: frequency
```

> The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown. Column order follows the order in the `select` expression.

With `sections: 3`, only the first three blocks are scored — roughly the introduction and first section of a markdown document:

```yaml
type: synopsis
source: ./table_plugin.md
max_sentences: 3
algorithm: frequency
sections: 3
```

> The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown.

> **Note:** `sections: 0` (the default) means all blocks are included. A value of `1` limits input to the very first paragraph or section.

## Block model and positional decay

The synopsis plugin treats blank lines as universal block separators — the same boundary that separates paragraphs in plain text and section bodies in markdown. Each block is assigned a positional weight:

```
block_weight = 1.0 / (1 + block_index)
final_score  = algorithm_score × block_weight
```

Block 0 (the introduction) scores at full weight. Later blocks decay geometrically. This consistently surfaces introductory material without requiring any format detection.
