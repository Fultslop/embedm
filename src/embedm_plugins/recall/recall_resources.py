from types import SimpleNamespace

str_resources = SimpleNamespace(
    note_no_recall_content="> [!NOTE]\n> No relevant content could be retrieved.",
    note_recall_fallback="> [!NOTE]\n> No sentences matched the query. Showing most representative sentences instead.",
    err_recall_query_required="'query' is required for the recall directive.",
    err_recall_max_sentences_min="'max_sentences' must be >= 1, got {value}.",
    err_recall_sections_min="'sections' must be >= 0, got {value}.",
    err_recall_invalid_language="invalid language '{value}'. Supported: {valid}.",
)
