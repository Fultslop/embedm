"""Unit tests for SynopsisPlugin — directive validation and transform."""

from collections.abc import Sequence

import pytest

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import StatusLevel
from embedm_plugins.synopsis_plugin import SynopsisPlugin

_PLUGIN = SynopsisPlugin()


def _directive(**options: str) -> Directive:
    return Directive(type="synopsis", options=dict(options))


def _leaf_node(directive: Directive) -> PlanNode:
    return PlanNode(directive=directive, status=[], document=None, children=None)


def _parent_doc(text: str) -> Sequence[Fragment]:
    return [text]


# ---------------------------------------------------------------------------
# validate_directive
# ---------------------------------------------------------------------------


def test_validate_directive_valid_defaults() -> None:
    errors = _PLUGIN.validate_directive(_directive())
    assert errors == []


def test_validate_directive_all_valid_options() -> None:
    errors = _PLUGIN.validate_directive(_directive(max_sentences="2", algorithm="luhn", language="nl"))
    assert errors == []


def test_validate_directive_invalid_max_sentences_type() -> None:
    errors = _PLUGIN.validate_directive(_directive(max_sentences="abc"))
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_max_sentences_zero() -> None:
    errors = _PLUGIN.validate_directive(_directive(max_sentences="0"))
    assert len(errors) == 1
    assert "max_sentences" in errors[0].description


def test_validate_directive_invalid_algorithm() -> None:
    errors = _PLUGIN.validate_directive(_directive(algorithm="textrank"))
    assert len(errors) == 1
    assert "textrank" in errors[0].description


def test_validate_directive_invalid_language() -> None:
    errors = _PLUGIN.validate_directive(_directive(language="fr"))
    assert len(errors) == 1
    assert "fr" in errors[0].description


def test_validate_directive_multiple_errors() -> None:
    errors = _PLUGIN.validate_directive(_directive(algorithm="bad", language="bad", max_sentences="0"))
    assert len(errors) == 3


def test_validate_directive_invalid_sections_type() -> None:
    errors = _PLUGIN.validate_directive(_directive(sections="abc"))
    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR


def test_validate_directive_sections_negative() -> None:
    errors = _PLUGIN.validate_directive(_directive(sections="-1"))
    assert len(errors) == 1
    assert "sections" in errors[0].description


def test_validate_directive_sections_zero_is_valid() -> None:
    errors = _PLUGIN.validate_directive(_directive(sections="0"))
    assert errors == []


# ---------------------------------------------------------------------------
# transform — no source (reads parent_document)
# ---------------------------------------------------------------------------


def test_transform_returns_blockquote() -> None:
    directive = _directive(max_sentences="1", algorithm="frequency", language="en")
    node = _leaf_node(directive)
    text = "Space exploration is fascinating. Mars is a red planet. Astronauts explore space on missions."
    result = _PLUGIN.transform(node, _parent_doc(text))
    assert result.startswith("> ")
    assert result.endswith("\n")


def test_transform_skips_directive_objects_in_parent_document() -> None:
    directive = _directive(max_sentences="2", algorithm="frequency", language="en")
    node = _leaf_node(directive)
    other_directive = Directive(type="toc")
    # parent_document contains a mix of str and Directive objects
    parent: Sequence[Fragment] = [
        "Space exploration is fascinating. Mars is a red planet. ",
        other_directive,
        "Astronauts explore space on missions.",
    ]
    result = _PLUGIN.transform(node, parent)
    assert result.startswith("> ")
    assert "Space" in result or "Astronauts" in result


def test_transform_uses_default_algorithm_and_language() -> None:
    directive = _directive()
    node = _leaf_node(directive)
    text = "Space exploration is fascinating. Mars is a red planet. Astronauts explore space on missions."
    result = _PLUGIN.transform(node, _parent_doc(text))
    assert result.startswith("> ")


def test_transform_empty_parent_document_returns_note() -> None:
    directive = _directive()
    node = _leaf_node(directive)
    result = _PLUGIN.transform(node, [])
    assert "[!NOTE]" in result


# ---------------------------------------------------------------------------
# transform — with source (reads file_cache)
# ---------------------------------------------------------------------------


class _FakeFileCache:
    def __init__(self, content: str) -> None:
        self._content = content
        self.max_embed_size = 0

    def get_file(self, path: str) -> tuple[str | None, list]:
        return self._content, []


def test_transform_with_source_reads_from_file_cache() -> None:
    directive = Directive(
        type="synopsis",
        source="somefile.txt",
        options={"max_sentences": "1", "algorithm": "frequency", "language": "en"},
    )
    node = _leaf_node(directive)
    file_text = "Space exploration is fascinating. Mars is a red planet. Astronauts explore space on missions."
    result = _PLUGIN.transform(node, [], file_cache=_FakeFileCache(file_text))  # type: ignore[arg-type]
    assert result.startswith("> ")
