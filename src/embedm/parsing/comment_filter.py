"""Comment filtering for extracted code snippets.

Removes full-line and trailing inline comments from code content, using the
language's CommentStyle to identify comment delimiters. String literals are
preserved — comment-like sequences inside strings are not treated as comments.
"""

from __future__ import annotations

from dataclasses import dataclass

from embedm.parsing.symbol_parser import CommentStyle


@dataclass
class _FilterState:
    """Tracks string and block-comment state across lines during filtering."""

    in_block_comment: bool = False
    in_string: bool = False
    string_char: str | None = None


def _step_block_comment(line: str, i: int, state: _FilterState, style: CommentStyle) -> int:
    end = style.block_comment_end
    if end and line[i : i + len(end)] == end:
        state.in_block_comment = False
        i += len(end)
    else:
        i += 1
    return i


def _step_string(line: str, i: int, state: _FilterState, real_chars: list[str]) -> int:
    if line[i] == "\\":
        real_chars.append(line[i])
        if i + 1 < len(line):
            real_chars.append(line[i + 1])
        i += 2
    else:
        if line[i] == state.string_char:
            state.in_string = False
            state.string_char = None
        real_chars.append(line[i])
        i += 1
    return i


def _step_code(line: str, i: int, state: _FilterState, style: CommentStyle, real_chars: list[str]) -> int | None:
    """Process one character in normal (non-comment, non-string) code mode.

    Returns the new index to continue scanning, or None if a comment was
    found and scanning should stop (truncate the line here).
    """
    lc = style.line_comment
    if lc and line[i : i + len(lc)] == lc:
        return None

    bc_start = style.block_comment_start
    if bc_start and line[i : i + len(bc_start)] == bc_start:
        state.in_block_comment = True
        return i + len(bc_start)

    if line[i] in style.string_delimiters:
        state.in_string = True
        state.string_char = line[i]

    real_chars.append(line[i])
    return i + 1


def _strip_line_comment(line: str, style: CommentStyle, state: _FilterState) -> tuple[str | None, _FilterState]:
    """Filter comments from a single line.

    Returns (filtered_line, new_state) where filtered_line is:
    - None if the entire line should be dropped (comment-only or inside a block comment)
    - The line with the trailing comment stripped (rstripped) if a comment was found
    - The original line if no comment was found

    Blank lines that are not inside a block comment are returned unchanged.
    """
    if not state.in_block_comment and not line.strip():
        return line, state

    real_chars: list[str] = []
    i = 0

    while i < len(line):
        if state.in_block_comment:
            i = _step_block_comment(line, i, state, style)
            continue
        if state.in_string:
            i = _step_string(line, i, state, real_chars)
            continue
        result = _step_code(line, i, state, style, real_chars)
        if result is None:
            break
        i = result

    filtered = "".join(real_chars).rstrip()
    return (None if not filtered.strip() else filtered), state


def filter_comments(content: str, style: CommentStyle) -> str:
    """Remove comments from code content using the given comment style.

    Full-line comments are dropped. Trailing inline comments are stripped from
    code lines. Blank lines are preserved. String literals containing
    comment-like sequences are not mangled.
    """
    lines = content.replace("\r\n", "\n").split("\n")
    state = _FilterState()
    result: list[str] = []
    for line in lines:
        filtered, state = _strip_line_comment(line, style, state)
        if filtered is not None:
            result.append(filtered)
    return "\n".join(result)
