# Recall Plugin

```yaml embedm
type: query-path
source: ../../../pyproject.toml
path: project.version
format: "version {value}"
```

The recall plugin retrieves the sentences from a document that are most relevant to a query. While the synopsis plugin summarises what a document is about, recall answers a specific question: *"which part of this document speaks to X?"*

This distinction matters most when a document is used as a knowledge source rather than read linearly — a reference manual, a technical spec, a meeting transcript, or a knowledge-base article. Embedding the whole document wastes context on irrelevant material; recall embeds only the passages that matter for the current question.

For an LLM like Claude this is particularly valuable. When a markdown document is assembled with embedm before being sent as context, a recall directive replaces a multi-page reference with the three or four sentences most relevant to what the reader (or the model) actually needs to know. The signal-to-noise ratio of the assembled context improves directly. This is offline retrieval-augmented generation — no vector database, no external service, no network dependency — just a static keyword query evaluated at compile time.

```yaml embedm
type: toc
add_slugs: True
```

## Basic Usage

Recall an external file by specifying `type: recall`, a `source` path, a `query`, and the maximum number of sentences to return. The plugin cleans the text (stripping code blocks, tables, and markdown formatting) before scoring. Output is always a blockquote.

```yaml
type: recall
source: ./synopsis_plugin.md
query: "how are sentences scored"
max_sentences: 2
```

```yaml embedm
type: recall
source: ./synopsis_plugin.md
query: "how are sentences scored"
max_sentences: 2
```

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

```yaml embedm
type: recall
source: ./synopsis_plugin.md
query: "block positional decay weight"
max_sentences: 2
```

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

```yaml embedm
type: synopsis
source: ./table_plugin.md
max_sentences: 2
algorithm: frequency
```

**Recall** — sentences from the same source about filtering:

```yaml
type: recall
source: ./table_plugin.md
query: "filter rows conditions operators"
max_sentences: 2
```

```yaml embedm
type: recall
source: ./table_plugin.md
query: "filter rows conditions operators"
max_sentences: 2
```

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

```yaml embedm
type: recall
source: ./table_plugin.md
query: "column selection rename alias"
max_sentences: 2
```

With `sections: 2`, only the first two blocks are considered:

```yaml
type: recall
source: ./table_plugin.md
query: "column selection rename alias"
max_sentences: 2
sections: 2
```

```yaml embedm
type: recall
source: ./table_plugin.md
query: "column selection rename alias"
max_sentences: 2
sections: 2
```

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

## Building an AI agent context document

Every AI coding session starts cold. Tools like Claude have no memory of previous decisions, established patterns, or project history unless that context is explicitly provided. Loading entire files is expensive; recall makes targeted context assembly affordable.

An agent context document is a compiled markdown file containing recall directives that pre-filter your project's knowledge sources — guidelines, a decision log, active work items — into a single focused reference. The AI reads the compiled output at session start and arrives with the right context rather than a blank slate.

### Step 1 — Identify your knowledge sources

Decide which files contain knowledge worth pre-filtering:

- **Guidelines** — coding standards, architectural rules, naming conventions
- **Decision log** — a chronological record of design decisions and corrections
- **Active spec** — the feature or task currently in progress

### Step 2 — Create a source document

Create a source file (e.g., `agent_context.src.md`) with one or more directives per knowledge category. Use `file` for short, complete documents you always want in full. Use `recall` for long documents where only the relevant passages matter.

For a guidelines file (short enough to embed whole):

```yaml
type: file
source: ./CLAUDE.md
```

For a long decision log (embed only the architecturally relevant passages):

```yaml
type: recall
source: ./devlog.md
query: "architectural decision convention rule established"
max_sentences: 6
```

For the active spec (full content needed):

```yaml
type: file
source: ./backlog/in_progress/current_feature.md
```

Use specific, technical queries — terms that only appear in the passages you actually want. Vague queries like `"how does it work"` produce noise; specific ones like `"validation transform boundary plugin pure"` produce signal.

### Step 3 — Compile

```
embedm agent_context.src.md agent_context.md
```

Review the compiled output. Each recall section should surface genuinely useful content. If a section looks wrong, refine the query: add domain-specific terms, remove ambiguous words, or adjust `max_sentences`.

### Step 4 — Point your agent to the compiled output

Tell the AI to read the compiled document at session start. For Claude Code, add a line to `CLAUDE.md`:

```
At the start of each session, read doc/project/agent_context.md before beginning any task.
```

### Step 5 — Recompile when sources change

The compiled document is a snapshot. Recompile it after significant additions to the decision log or when the active spec changes. A stale context document is still useful, but a current one is better.

### Step 6 — Track misses and tune queries

When the agent makes an error the context document should have prevented, record it — for example with a `[MISS]` tag in the decision log. After a few sessions, review the misses: are they clustered around a knowledge category the document does not cover? If so, add or tune a recall directive to target that gap.

### Step 7 — Maintain the knowledge base

Recall quality degrades as source documents grow. A decision log with hundreds of entries will produce noisier results than one with fifty. Periodic archiving keeps queries sharp.

Before archiving a batch of entries, create a temporary source document to run what is called the *promotion gate*: a recall over the entries to be archived, looking for decisions that were recorded but never formally captured as rules.

```yaml
type: recall
source: ./devlog.md
query: "convention rule architectural decision established"
max_sentences: 8
```

Compile it and review the output. Any surfaced decision not already in your guidelines file should be added before archiving. Then manually move the old entries to an archive file — they remain searchable if you later add a recall directive over the archive for deep history.

This process ensures that archiving removes noise without removing knowledge.

### Keeping the bootstrap file minimal

If you use a tool like Claude Code, the agent automatically reads `.claude/CLAUDE.md` at session start. That file therefore has two jobs: holding rules and bootstrapping the context document. As your guidelines grow, these two jobs pull in opposite directions — you want the auto-read file to be small and fast, but the rules keep accumulating.

The solution is to separate them:

- **Bootstrap file** (`.claude/CLAUDE.md`) — hard constraints, platform notes, and the session-start pointer only. Stays small permanently.
- **Guidelines file** (`doc/project/guidelines.md`) — the full coding rules, architecture decisions, tooling standards. Grows freely.
- **Context document source** (`agent_context.src.md`) — embeds `guidelines.md`, not the bootstrap file.

The bootstrap file shrinks to roughly twenty lines. The guidelines file is the authoritative rules source. The agent context document compiles the guidelines plus targeted recall sections from the decision log. The relationship is clean and one-directional:

```
bootstrap → agent_context ← guidelines
                 ↑ (recall)
              devlog
```

Without this split there is a circular feeling: the auto-read file instructs the agent to read a compiled document that embeds the auto-read file back. The split removes that loop and makes each file's purpose unambiguous.

**Recommendation** 

As mentioned this requires capturing activities during the project. We keep a 'devlog.md' in the Embedm project. To see if the agent_context.md adds value, keep track of "misses" by the agent, ie actions that resulted in wrong outcomes or errors. Utilizing the agent_context should recude the number of misses over time. Note that this is a working hypothesis, a full controlled test is outside the scope.

In other words, the recall plugin is the glue: it turns a growing, noisy log into a focused, readable signal at a moment you choose. The [MISS] feedback loop closes it — misses tell you when the queries need tuning.
