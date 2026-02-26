"""Transformer that removes comments from extracted code content."""

from __future__ import annotations

from dataclasses import dataclass

from embedm.parsing.comment_filter import filter_comments
from embedm.parsing.symbol_parser import CommentStyle


@dataclass
class CommentFilterParams:
    """Parameters for comment filtering."""

    content: str
    style: CommentStyle


class CommentFilterTransformer:
    """Removes full-line and trailing inline comments from code content."""

    def execute(self, params: CommentFilterParams) -> str:
        """Return content with comments removed."""
        return filter_comments(params.content, params.style)
