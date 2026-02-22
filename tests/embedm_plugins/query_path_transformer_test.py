from embedm_plugins.query_path_transformer import QueryPathTransformer, QueryPathTransformerParams


def _run(value: object, raw_content: str = "", lang_tag: str = "json", is_full_document: bool = False) -> str:
    return QueryPathTransformer().execute(
        QueryPathTransformerParams(value=value, raw_content=raw_content, lang_tag=lang_tag, is_full_document=is_full_document)
    )


# --- scalar values ---


def test_string_scalar():
    assert _run("1.2.3") == "1.2.3"


def test_integer_scalar():
    assert _run(42) == "42"


def test_float_scalar():
    assert _run(3.14) == "3.14"


def test_bool_true():
    assert _run(True) == "true"


def test_bool_false():
    assert _run(False) == "false"


def test_null_value():
    assert _run(None) == "null"


def test_scalar_has_no_trailing_newline():
    result = _run("hello")
    assert not result.endswith("\n")


# --- dict / list values ---


def test_dict_value_produces_yaml_block():
    result = _run({"key": "value"})
    assert result.startswith("```yaml\n")
    assert result.endswith("\n```")
    assert "key: value" in result


def test_list_value_produces_yaml_block():
    result = _run([1, 2, 3])
    assert result.startswith("```yaml\n")
    assert "- 1" in result


# --- full document embed ---


def test_full_document_json():
    raw = '{"version": "1.0"}'
    result = _run(None, raw_content=raw, lang_tag="json", is_full_document=True)
    assert result == f"```json\n{raw}\n```"


def test_full_document_yaml():
    raw = "version: 1.0"
    result = _run(None, raw_content=raw, lang_tag="yaml", is_full_document=True)
    assert result == f"```yaml\n{raw}\n```"


def test_full_document_xml():
    raw = "<root/>"
    result = _run(None, raw_content=raw, lang_tag="xml", is_full_document=True)
    assert result == f"```xml\n{raw}\n```"


def test_full_document_strips_trailing_whitespace():
    raw = "version: 1.0\n\n"
    result = _run(None, raw_content=raw, lang_tag="yaml", is_full_document=True)
    assert result == "```yaml\nversion: 1.0\n```"
