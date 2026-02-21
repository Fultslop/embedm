FEATURE: Synopsis plugin
========================================
DRAFT  
Release v1.0  
Created: 20/02/2026  
Closed: `<date>`  
Created by: FS

## Description

Create a plugin that generates a deterministic synopsis of the current document or the document referred to in the `source` option of corresponding `Directive`. 

Directive definition:

```yaml embedm
type: synopsis
source: optional, if not defined take current document otherwise create a synopsis of source. Text files like .md, .txt are supported (others ?)
max_lines: maximum number of lines of the synopsis. Need to try to see what makes sense.
algorithm: Luhn, TextRank, Custom Frequency, MaxEnt / Statistical. Start with the simplest first for this version. Need at least two options. Discuss.
```

Notes: needs to execute before ToC

## Acceptance criteria

* The plugin creates a human readable synopsis that captures the source / current document correctly.

* The plugin is part of the standard plugins (like hello_world, file, table...)

* We have associated unit and integration tests.

* We have associated regression tests.

* Documentation is out of scope for now.

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

Architecture concerns

"Current document" mode (no source) — the planner's _build_children already filters out sourceless directives (if d.source), so a sourceless synopsis directive stays as a leaf. At transform time parent_document.content is available, so the plugin can summarise it directly. No planner changes needed. However, the content at that point is the raw source markdown, not the rendered output. The synopsis would describe the un-resolved document, which may include embed directives rather than their content. Worth flagging in the spec.

Sentence splitting — simple regex ([.!?]\s+ or end-of-string) works for prose. Markdown headings and list items need special handling. Stripping markdown syntax before tokenisation (code fences, link syntax, heading markers) is the right approach; pure-regex for v1 is fine.

max_lines vs max_sentences — both algorithms work at sentence granularity. max_sentences is more natural internally; the spec could expose it as max_sentences or translate max_lines by estimating average sentence length. Worth settling before implementation.

Plugin ordering — the spec correctly notes it must run before ToC. The default plugin_sequence would need synopsis inserted before toc_plugin.

"Deterministic" — both Frequency and Luhn are deterministic if ties are broken by original sentence index. Should be documented as a constraint on any algorithm added later.

What would help clarify the spec before implementation:

Should the "current document" summarise raw source or post-embed-resolution text? (The former is free; the latter requires the plugin to run after compilation, which conflicts with "before ToC".)
max_lines or max_sentences — pick one.
Should markdown formatting (code blocks, tables) be excluded from summarisation input?
Is English-only acceptable for v1, or does the stopword list need to be configurable?

**21/02/2026** FS:

1. it should be post embed, and run before ToC to avoid including the Toc in the algorithm/word count. Maybe skip ```yaml embedm blocks ?
2. max_sentences
3. They usually serve as examples, so I'd say yes exclude themm
4. Good point. Let's include two languages English and  Dutch to demonstrate configurability UNLESS that blows up the scope beyond reason.