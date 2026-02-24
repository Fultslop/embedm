from __future__ import annotations

from collections.abc import Sequence

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.directive_options import get_option, validate_option
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_context import PluginContext
from embedm_plugins.recall_resources import str_resources
from embedm_plugins.recall_transformer import RecallParams, RecallTransformer

MAX_SENTENCES_KEY = "max_sentences"
LANGUAGE_KEY = "language"
SECTIONS_KEY = "sections"
QUERY_KEY = "query"

_DEFAULT_MAX_SENTENCES = 3
_DEFAULT_LANGUAGE = "en"
_DEFAULT_SECTIONS = 0

_VALID_LANGUAGES: frozenset[str] = frozenset({"en", "nl"})


class RecallPlugin(PluginBase):
    """Retrieve the most relevant sentences from a document for a given query."""

    name = "recall plugin"
    api_version = 1
    directive_type = "recall"

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        """Validate recall directive options."""
        assert directive is not None, "directive is required — orchestration must provide it"

        statuses: list[Status] = []

        if not directive.options.get(QUERY_KEY):
            statuses.append(Status(StatusLevel.ERROR, str_resources.err_recall_query_required))

        statuses.extend(
            _validate_int_min(
                directive, MAX_SENTENCES_KEY, _DEFAULT_MAX_SENTENCES, 1, str_resources.err_recall_max_sentences_min
            )
        )
        statuses.extend(
            _validate_enum(directive, LANGUAGE_KEY, _VALID_LANGUAGES, str_resources.err_recall_invalid_language)
        )
        statuses.extend(
            _validate_int_min(directive, SECTIONS_KEY, _DEFAULT_SECTIONS, 0, str_resources.err_recall_sections_min)
        )
        return statuses

    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        context: PluginContext | None = None,
    ) -> str:
        """Transform a recall directive into a GFM blockquote of relevant sentences."""
        text = _extract_text(plan_node, parent_document, context.file_cache if context else None)
        query = get_option(plan_node.directive, QUERY_KEY, cast=str, default_value="")
        max_sentences = get_option(
            plan_node.directive, MAX_SENTENCES_KEY, cast=int, default_value=_DEFAULT_MAX_SENTENCES
        )
        language = get_option(plan_node.directive, LANGUAGE_KEY, cast=str, default_value=_DEFAULT_LANGUAGE)
        sections = get_option(plan_node.directive, SECTIONS_KEY, cast=int, default_value=_DEFAULT_SECTIONS)
        return RecallTransformer().execute(RecallParams(text, query, max_sentences, language, sections))


def _extract_text(plan_node: PlanNode, parent_document: Sequence[Fragment], file_cache: FileCache | None) -> str:
    """Return raw text to summarise: source file content or joined parent_document string fragments."""
    if plan_node.directive.source:
        assert file_cache is not None, "file_cache is required when directive has a source"
        content, _ = file_cache.get_file(plan_node.directive.source)
        return content or ""
    return "".join(fragment for fragment in parent_document if isinstance(fragment, str))


def _validate_int_min(
    directive: Directive, key: str, default: int, min_value: int, error_template: str
) -> list[Status]:
    """Validate that an integer directive option meets a minimum value."""
    if (status := validate_option(directive, key, cast=int)) is not None:
        return [status]
    value = get_option(directive, key, cast=int, default_value=default)
    if value < min_value:
        return [Status(StatusLevel.ERROR, error_template.format(value=value))]
    return []


def _validate_enum(directive: Directive, key: str, valid: frozenset[str], error_template: str) -> list[Status]:
    """Validate a string directive option against a set of allowed values."""
    value = directive.options.get(key)
    if value is not None and value not in valid:
        return [Status(StatusLevel.ERROR, error_template.format(value=value, valid=", ".join(sorted(valid))))]
    return []
