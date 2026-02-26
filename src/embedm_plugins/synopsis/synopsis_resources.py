from types import SimpleNamespace

str_resources = SimpleNamespace(
    note_no_synopsis_content="> [!NOTE]\n> No summary could be generated.",
    err_synopsis_invalid_algorithm="invalid algorithm '{value}'. Supported: {valid}.",
    err_synopsis_invalid_language="invalid language '{value}'. Supported: {valid}.",
    err_synopsis_max_sentences_min="'max_sentences' must be >= 1, got {value}.",
    err_synopsis_sections_min="'sections' must be >= 0, got {value}.",
)
