from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_util import to_relative
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_context import PluginContext
from embedm.plugins.validation_base import ValidationResult
from embedm_plugins import query_path_engine as engine
from embedm_plugins import query_path_normalize_json as normalize_json
from embedm_plugins import query_path_normalize_toml as normalize_toml
from embedm_plugins import query_path_normalize_xml as normalize_xml
from embedm_plugins import query_path_normalize_yaml as normalize_yaml
from embedm_plugins.query_path_resources import str_resources
from embedm_plugins.query_path_transformer import QueryPathTransformer, QueryPathTransformerParams

_SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({"json", "yaml", "yml", "xml", "toml"})
_EXT_TO_LANG_TAG: dict[str, str] = {"json": "json", "yaml": "yaml", "yml": "yaml", "xml": "xml", "toml": "toml"}


@dataclass
class _QueryPathArtifact:
    value: Any
    raw_content: str
    lang_tag: str
    is_full_document: bool
    format_str: str | None = None


def _get_ext(source: str) -> str:
    return Path(source).suffix.lower().lstrip(".")


def _parse(content: str, ext: str) -> Any:
    if ext == "json":
        return normalize_json.normalize(content)
    if ext in ("yaml", "yml"):
        return normalize_yaml.normalize(content)
    if ext == "toml":
        return normalize_toml.normalize(content)
    return normalize_xml.normalize(content)


def _parse_error_message(ext: str, exc: Exception) -> str:
    if ext == "json":
        return str(str_resources.err_query_path_invalid_json.format(exc=exc))
    if ext in ("yaml", "yml"):
        return str(str_resources.err_query_path_invalid_yaml.format(exc=exc))
    if ext == "toml":
        return str(str_resources.err_query_path_invalid_toml.format(exc=exc))
    return str(str_resources.err_query_path_invalid_xml.format(exc=exc))


class QueryPathPlugin(PluginBase):
    """Plugin that extracts and embeds a value from a JSON, YAML, or XML file using a dot-notation path."""

    name = "query path plugin"
    api_version = 1
    directive_type = "query-path"

    def validate_directive(
        self, directive: Directive, _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        """Validate that source is present and its extension is supported."""
        assert directive is not None, "directive is required — orchestration must provide it"

        if not directive.source:
            return [Status(StatusLevel.ERROR, str_resources.err_query_path_missing_source)]

        ext = _get_ext(directive.source)
        if ext not in _SUPPORTED_EXTENSIONS:
            return [Status(StatusLevel.ERROR, str_resources.err_query_path_unsupported_format.format(ext=ext))]

        format_str = directive.options.get("format", "")
        if format_str and not directive.options.get("path", ""):
            return [Status(StatusLevel.ERROR, str_resources.err_query_path_format_requires_path)]
        if format_str and "{value}" not in format_str:
            return [Status(StatusLevel.ERROR, str_resources.err_query_path_format_missing_placeholder)]

        return []

    def validate_input(
        self,
        directive: Directive,
        content: str,
        _plugin_config: PluginConfiguration | None = None,
    ) -> ValidationResult[_QueryPathArtifact]:
        """Parse source file and resolve the query path. Returns the resolved value as artifact."""
        assert directive is not None, "directive is required"
        assert content is not None, "content is required"

        ext = _get_ext(directive.source)
        lang_tag = _EXT_TO_LANG_TAG.get(ext, ext)
        path_str = directive.options.get("path", "")
        format_str: str | None = directive.options.get("format") or None

        try:
            tree = _parse(content, ext)
        except Exception as exc:
            return ValidationResult(artifact=None, errors=[Status(StatusLevel.ERROR, _parse_error_message(ext, exc))])

        if not path_str:
            return ValidationResult(
                artifact=_QueryPathArtifact(value=None, raw_content=content, lang_tag=lang_tag, is_full_document=True)
            )

        segments = engine.parse_path(path_str)
        try:
            value = engine.resolve(tree, segments)
        except (KeyError, IndexError):
            error = Status(
                StatusLevel.ERROR,
                str_resources.err_query_path_not_found.format(path=path_str, source=to_relative(directive.source)),
            )
            return ValidationResult(artifact=None, errors=[error])

        if format_str and isinstance(value, (dict, list)):
            error = Status(StatusLevel.ERROR, str_resources.err_query_path_format_non_scalar)
            return ValidationResult(artifact=None, errors=[error])

        return ValidationResult(
            artifact=_QueryPathArtifact(
                value=value, raw_content=content, lang_tag=lang_tag, is_full_document=False, format_str=format_str
            )
        )

    def transform(
        self,
        plan_node: PlanNode,
        _parent_document: Sequence[Fragment],
        _context: PluginContext | None = None,
    ) -> str:
        """Render the resolved query result as a string."""
        if plan_node.document is None:
            return ""

        artifact: _QueryPathArtifact | None = plan_node.artifact
        if artifact is None:
            return ""

        return QueryPathTransformer().execute(
            QueryPathTransformerParams(
                value=artifact.value,
                raw_content=artifact.raw_content,
                lang_tag=artifact.lang_tag,
                is_full_document=artifact.is_full_document,
                format_str=artifact.format_str,
            )
        )
