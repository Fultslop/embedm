from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

import yaml

from embedm.plugins.transformer_base import TransformerBase


@dataclass
class QueryPathTransformerParams:
    """Parameters for the query path transformer."""

    value: Any
    raw_content: str
    lang_tag: str
    is_full_document: bool


class QueryPathTransformer(TransformerBase[QueryPathTransformerParams]):
    """Renders a resolved query result as inline text or a fenced code block."""

    params_type: ClassVar[type[QueryPathTransformerParams]] = QueryPathTransformerParams

    def execute(self, params: QueryPathTransformerParams) -> str:
        """Transform the resolved value into its final string representation."""
        assert params is not None, "params must not be None"

        if params.is_full_document:
            return f"```{params.lang_tag}\n{params.raw_content.rstrip()}\n```"

        return _render_value(params.value)


def _render_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    dumped = yaml.dump(value, default_flow_style=False, allow_unicode=True).rstrip()
    return f"```yaml\n{dumped}\n```"
