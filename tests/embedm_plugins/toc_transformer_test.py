from embedm_plugins.plugin_resources import str_resources
from embedm_plugins.toc_transformer import ToCParams, ToCTransformer


def test_transformer_execute_with_empty_content():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=[], max_depth=1, add_slugs=False)

    assert transformer.execute(params) == str_resources.note_no_toc_content


def test_transformer_execute_with_single_header():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=["## header"], max_depth=10, add_slugs=False)

    assert transformer.execute(params) == "  - header"


def test_transformer_execute_with_multiple_headers_in_single_fragment():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=["## header 1\n### header 2"], max_depth=10, add_slugs=False)

    assert transformer.execute(params) == "  - header 1\n    - header 2"


def test_transformer_execute_with_multiple_headers_in_multiple_fragments():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=["## header 1", "### header 2"], max_depth=10, add_slugs=False)

    assert transformer.execute(params) == "  - header 1\n    - header 2"


def test_transformer_execute_with_fenced_header():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=["```pre\n## header\n```"], max_depth=10, add_slugs=False)

    assert transformer.execute(params) == str_resources.note_no_toc_content


def test_transformer_execute_with_slug():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=["## header name\nlorem ipsum"], max_depth=10, add_slugs=True)

    assert transformer.execute(params) == "  - [header name](#header-name)"


def test_transformer_execute_with_max_depth():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=["## header 2a\n### header 3\n## header 2b"], max_depth=2, add_slugs=False)

    # header 3 should have been ignored
    assert transformer.execute(params) == "  - header 2a\n  - header 2b"


def test_transformer_execute_with_non_unique_anchors():
    transformer = ToCTransformer()
    params = ToCParams(parent_document=["## header name\n## header name"], max_depth=10, add_slugs=True)

    # second 'header name' should have a -1 in added to the slug
    assert transformer.execute(params) == "  - [header name](#header-name)\n  - [header name](#header-name-1)"
