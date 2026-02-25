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
from embedm_plugins.synopsis.synopsis_resources import str_resources
from embedm_plugins.synopsis.synopsis_transformer import SynopsisParams, SynopsisTransformer

MAX_SENTENCES_KEY = "max_sentences"
ALGORITHM_KEY = "algorithm"
LANGUAGE_KEY = "language"
SECTIONS_KEY = "sections"

_DEFAULT_MAX_SENTENCES = 3
_DEFAULT_ALGORITHM = "frequency"
_DEFAULT_LANGUAGE = "en"
_DEFAULT_SECTIONS = 0

_VALID_ALGORITHMS: frozenset[str] = frozenset({"frequency", "luhn"})
_VALID_LANGUAGES: frozenset[str] = frozenset({"en", "nl"})


class SynopsisPlugin(PluginBase):
    name = "synopsis plugin"
    api_version = 1
    directive_type = "synopsis"

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        assert directive is not None, "directive is required — orchestration must provide it"

        statuses: list[Status] = []
        statuses.extend(
            _validate_int_min(
                directive, MAX_SENTENCES_KEY, _DEFAULT_MAX_SENTENCES, 1, str_resources.err_synopsis_max_sentences_min
            )
        )
        statuses.extend(
            _validate_enum(directive, ALGORITHM_KEY, _VALID_ALGORITHMS, str_resources.err_synopsis_invalid_algorithm)
        )
        statuses.extend(
            _validate_enum(directive, LANGUAGE_KEY, _VALID_LANGUAGES, str_resources.err_synopsis_invalid_language)
        )
        statuses.extend(
            _validate_int_min(directive, SECTIONS_KEY, _DEFAULT_SECTIONS, 0, str_resources.err_synopsis_sections_min)
        )
        return statuses

    def transform(
        self,
        plan_node: PlanNode,
        parent_document: Sequence[Fragment],
        context: PluginContext | None = None,
    ) -> str:
        text = _extract_text(plan_node, parent_document, context.file_cache if context else None)
        max_sentences = get_option(
            plan_node.directive, MAX_SENTENCES_KEY, cast=int, default_value=_DEFAULT_MAX_SENTENCES
        )
        algorithm = get_option(plan_node.directive, ALGORITHM_KEY, cast=str, default_value=_DEFAULT_ALGORITHM)
        language = get_option(plan_node.directive, LANGUAGE_KEY, cast=str, default_value=_DEFAULT_LANGUAGE)
        sections = get_option(plan_node.directive, SECTIONS_KEY, cast=int, default_value=_DEFAULT_SECTIONS)
        return SynopsisTransformer().execute(SynopsisParams(text, max_sentences, algorithm, language, sections))


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
