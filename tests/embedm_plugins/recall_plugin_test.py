"""Unit tests for RecallPlugin — directive validation and transform."""

from collections.abc import Sequence

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import StatusLevel
from embedm.plugins.plugin_context import PluginContext
from embedm_plugins.recall_plugin import RecallPlugin

_PLUGIN = RecallPlugin()

_TEXT = (
    "Authentication handles user login and session management.\n\n"
    "The database stores user credentials securely.\n\n"
    "Caching improves response times for repeated requests."
)


def _directive(**options: str) -> Directive:
    return Directive(type="recall", options=dict(options))


def _leaf_node(directive: Directive) -> PlanNode:
    return PlanNode(directive=directive, status=[], document=None, children=None)


def _parent_doc(text: str) -> Sequence[Fragment]:
    return [text]


# ---------------------------------------------------------------------------
# validate_directive
# ---------------------------------------------------------------------------


def test_validate_directive_missing_query_returns_error() -> None:
    errors = _PLUGIN.validate_directive(_directive())
    assert any("query" in e.description.lower() for e in errors)
    assert any(e.level == StatusLevel.ERROR for e in errors)


def test_validate_directive_empty_query_returns_error() -> None:
    errors = _PLUGIN.validate_directive(_directive(query=""))
    assert any("query" in e.description.lower() for e in errors)


def test_validate_directive_valid_query_no_error() -> None:
    errors = _PLUGIN.validate_directive(_directive(query="authentication"))
    assert errors == []


def test_validate_directive_all_valid_options() -> None:
    errors = _PLUGIN.validate_directive(
        _directive(query="test", max_sentences="2", language="nl", sections="3")
    )
    assert errors == []


def test_validate_directive_invalid_max_sentences_type() -> None:
    errors = _PLUGIN.validate_directive(_directive(query="test", max_sentences="abc"))
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_max_sentences_zero() -> None:
    errors = _PLUGIN.validate_directive(_directive(query="test", max_sentences="0"))
    assert len(errors) == 1
    assert "max_sentences" in errors[0].description


def test_validate_directive_invalid_language() -> None:
    errors = _PLUGIN.validate_directive(_directive(query="test", language="fr"))
    assert len(errors) == 1
    assert "fr" in errors[0].description


def test_validate_directive_invalid_sections_type() -> None:
    errors = _PLUGIN.validate_directive(_directive(query="test", sections="abc"))
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_sections_negative() -> None:
    errors = _PLUGIN.validate_directive(_directive(query="test", sections="-1"))
    assert len(errors) == 1
    assert "sections" in errors[0].description


def test_validate_directive_sections_zero_is_valid() -> None:
    errors = _PLUGIN.validate_directive(_directive(query="test", sections="0"))
    assert errors == []


# ---------------------------------------------------------------------------
# transform — no source (reads parent_document)
# ---------------------------------------------------------------------------


def test_transform_returns_blockquote() -> None:
    directive = _directive(query="authentication session", max_sentences="1")
    node = _leaf_node(directive)
    result = _PLUGIN.transform(node, _parent_doc(_TEXT))
    assert result.startswith("> ")
    assert result.endswith("\n")


def test_transform_uses_default_max_sentences() -> None:
    directive = _directive(query="authentication")
    node = _leaf_node(directive)
    result = _PLUGIN.transform(node, _parent_doc(_TEXT))
    assert result.startswith("> ")


def test_transform_empty_content_returns_note() -> None:
    directive = _directive(query="authentication")
    node = _leaf_node(directive)
    result = _PLUGIN.transform(node, [])
    assert "[!NOTE]" in result


def test_transform_skips_directive_objects_in_parent_document() -> None:
    directive = _directive(query="authentication session", max_sentences="1")
    node = _leaf_node(directive)
    other = Directive(type="toc")
    parent: Sequence[Fragment] = [
        "Authentication handles user login and session management.\n\n",
        other,
        "Caching improves response times for repeated requests.",
    ]
    result = _PLUGIN.transform(node, parent)
    assert result.startswith("> ")


# ---------------------------------------------------------------------------
# transform — with source (reads file_cache)
# ---------------------------------------------------------------------------


class _FakeFileCache:
    def __init__(self, content: str) -> None:
        self._content = content
        self.max_embed_size = 0

    def get_file(self, path: str) -> tuple[str | None, list]:  # type: ignore[type-arg]
        return self._content, []


def test_transform_with_source_reads_from_file_cache() -> None:
    directive = Directive(
        type="recall",
        source="somefile.md",
        options={"query": "authentication session", "max_sentences": "1"},
    )
    node = _leaf_node(directive)
    result = _PLUGIN.transform(node, [], PluginContext(_FakeFileCache(_TEXT)))  # type: ignore[arg-type]
    assert result.startswith("> ")
    assert result.endswith("\n")
