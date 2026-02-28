FEATURE: Synopsis — LLM-based summarization
========================================
Draft
Created: 21/02/2026
Closed: `<date>`
Created by: FS

## Description

Add `algorithm: llm` to the synopsis plugin, delegating summarization to a large language model via an external API.

The statistical algorithms (frequency, Luhn, TextRank) extract sentences that already exist in the document. An LLM generates a genuinely abstractive summary — it can paraphrase, merge ideas across sentences, and produce output that reads as natural prose rather than a stitched-together sentence sequence. Quality is significantly higher for complex or nuanced documents.

**Approach:**

- Clean the input text using the existing `_clean_text` pipeline.
- Optionally apply the `sections` cap to reduce the context sent to the API.
- Send the cleaned text to the configured LLM with a prompt such as:
  `"Summarize the following in {max_sentences} sentences:\n\n{text}"`
- Return the response wrapped in a blockquote (same output format as existing algorithms).
- On API failure, emit a caution note rather than crashing.

**Configuration:**

API credentials and model selection should be read from the embedm config file or environment variables — not the directive. The directive only specifies `algorithm: llm`; the plugin resolves the provider and credentials at runtime.

```yaml
# embedm-config.yaml
llm:
  provider: anthropic         # or: openai
  model: claude-haiku-4-5-20251001
  api_key_env: ANTHROPIC_API_KEY
```

**Constraints:**

- Requires a network connection and a valid API key.
- Output is non-deterministic (LLM responses vary between calls); regression tests cannot use snapshot comparison — they should validate format only (starts with `> `, ends with `\n`).
- The `language` option passes the target language to the LLM prompt rather than selecting a stopword list.

## Acceptance criteria

- `algorithm: llm` is a valid directive value
- API provider and credentials are configured globally, not per-directive
- On API error (network failure, invalid key, rate limit), the plugin emits a caution note and does not raise
- `sections` and `max_sentences` options work with the LLM path
- `language` option is forwarded to the prompt
- Unit tests mock the API call; integration tests are optional and skipped without credentials
- Documentation notes the non-determinism and the config requirement

## Comments

`21/02/2026 FS/Claude:` Identified during synopsis quality review. Best suited for user-facing summaries where quality matters more than offline operation or reproducibility. The clean-then-cap-then-summarize pipeline (using `_clean_text` + `sections`) reduces token usage significantly for large documents. Consider a `max_tokens` or `context_limit` config option to prevent oversized API calls.
