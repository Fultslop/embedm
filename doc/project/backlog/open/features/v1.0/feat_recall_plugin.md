FEATURE: Recall plugin — query-based context retrieval
========================================
Draft  
Release v1.0  
Created: 22/02/2026  
Closed: `<date>`  
Created by: Claude  

## Description

A plugin that retrieves the most relevant sentences from a document for a given query string, outputting them as a blockquote — the same output format as the synopsis plugin. Where `synopsis` surfaces the most representative sentences for the whole document, `recall` surfaces the most relevant sentences for a specific question or topic.

This is an **offline RAG (Retrieval-Augmented Generation) retrieval step** with no external dependencies. Its primary use case is assembling focused context for LLM agents and prompts: given a large reference document, embed only the passages most relevant to the current task.

Directive definition:

```yaml embedm
type: recall
source: ./large_reference.md
query: "authentication and session management"
max_sentences: 5
language: en
sections: 0
```

### Behaviour

- `source` or current-document mode, same as synopsis.
- `query` is required. It is tokenised and stop-word filtered using the same pipeline as synopsis.
- Scoring: sentences are scored by the **overlap between their significant tokens and the query tokens**, rather than document-wide frequency. Specifically, the score for sentence `s` is:

  ```
  query_tokens = significant tokens in query (after stopword filter)
  overlap(s) = |tokens(s) ∩ query_tokens| / |query_tokens|
  block_weight = 1.0 / (1 + block_index)
  final_score = overlap(s) × block_weight
  ```

- Block positional decay applies: earlier blocks score higher when overlap is equal.
- `sections` caps the input to the first N blocks (same as synopsis).
- `language` selects the stopword list.
- If no sentences have any query overlap, the plugin falls back to a `synopsis`-style frequency score and notes the fallback.
- Output: a GFM blockquote, same as synopsis.

### Architecture

- Can share the `_clean_text`, `_split_into_blocks`, `_block_to_sentences`, `_tokenize` pipeline from `synopsis_transformer.py`.
- The scoring function is new but small: query token overlap rather than document frequency.
- Plugin sequence: same pass as synopsis (after `file`, before `toc`).
- New directive type: `recall`.

### AI / agent use cases

- An agent building a prompt assembles context by calling embedm with a recall directive, pulling the most relevant passages from a large document without loading the whole thing.
- A CLAUDE.md-style instruction file can embed focused extracts: "Here is the relevant architecture context for this task: [recall from architecture.md, query='plugin lifecycle']"
- Prompt templates can include recall directives that are resolved offline before the prompt is sent to the model, keeping token usage low.
- Knowledge bases and wikis become queryable without a vector database: embedm acts as a lightweight retrieval layer over a flat set of markdown files.

## Acceptance criteria

- `query` option is required; missing query → error caution block
- Sentences with higher query token overlap score above sentences with no overlap
- Block positional decay applies after overlap scoring
- `sections` and `language` options behave identically to the synopsis plugin
- Fallback to frequency scoring when no sentences match the query, with a note in the output
- Source and current-document modes both work
- Unit tests: correct overlap scoring, block decay, fallback behaviour
- Regression example using a non-trivial source document and a specific query

## Comments

`22/02/2026 FS/Claude:` This plugin is what makes embedm genuinely useful in an AI/agent workflow. The synopsis plugin already established the infrastructure; recall is a scoring variation, not a new architecture. The "no vector database" angle is the key differentiator — it works entirely offline on flat markdown files, making it viable in CI pipelines and agent context assembly scripts. Future extension: support multiple queries weighted by priority.
