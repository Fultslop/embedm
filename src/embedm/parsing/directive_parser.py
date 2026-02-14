import re
from typing import NamedTuple

import yaml

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.span import Span
from embedm.domain.status_level import Status, StatusLevel

EMBEDM_FENCE_PATTERN = re.compile(r"^```yaml embedm\s*$", re.MULTILINE)
CLOSING_FENCE_PATTERN = re.compile(r"^```\s*$", re.MULTILINE)

DIRECTIVE_TYPE_KEY = "type"
DIRECTIVE_SOURCE_KEY = "source"


class RawDirectiveBlock(NamedTuple):
    """A raw embedm block found in markdown content."""

    raw_content: str
    start: int
    end: int


def parse_yaml_embed_block(content: str) -> tuple[Directive | None, list[Status]]:
    """Parse a YAML string into a Directive."""
    if not content.strip():
        return None, [Status(StatusLevel.ERROR, "empty embedm block")]

    try:
        parsed = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        return None, [Status(StatusLevel.ERROR, f"invalid YAML in embedm block: {exc}")]

    if not isinstance(parsed, dict):
        return None, [Status(StatusLevel.ERROR, "embedm block must contain YAML key-value pairs")]

    if DIRECTIVE_TYPE_KEY not in parsed:
        return None, [Status(StatusLevel.ERROR, "embedm block is missing required 'type' field")]

    directive_type = str(parsed[DIRECTIVE_TYPE_KEY])
    source = str(parsed.get(DIRECTIVE_SOURCE_KEY, ""))
    options = {
        str(k): str(v)
        for k, v in parsed.items()
        if k not in (DIRECTIVE_TYPE_KEY, DIRECTIVE_SOURCE_KEY)
    }

    return Directive(type=directive_type, source=source, options=options), []


def find_yaml_embed_block(content: str) -> RawDirectiveBlock | None:
    """Find the first embedm block in markdown content."""
    opening = EMBEDM_FENCE_PATTERN.search(content)
    if opening is None:
        return None

    content_start = opening.end() + 1  # skip the newline after opening fence
    closing = CLOSING_FENCE_PATTERN.search(content, content_start)
    if closing is None:
        return None

    raw_content = content[content_start : closing.start()]
    block_end = closing.end() + 1 if closing.end() < len(content) else closing.end()

    return RawDirectiveBlock(
        raw_content=raw_content,
        start=opening.start(),
        end=block_end,
    )


def _find_all_raw_blocks(
    content: str,
) -> tuple[list[RawDirectiveBlock], list[Status], int]:
    """
    Find all raw embedm blocks in content. Returns blocks, errors,
    and the content end position.
    """
    blocks: list[RawDirectiveBlock] = []
    errors: list[Status] = []
    position = 0

    while position < len(content):
        opening = EMBEDM_FENCE_PATTERN.search(content, position)
        if opening is None:
            break

        content_start = opening.end() + 1
        closing = CLOSING_FENCE_PATTERN.search(content, content_start)

        if closing is None:
            errors.append(Status(StatusLevel.ERROR, "unclosed embedm block"))
            return blocks, errors, opening.start()

        raw_content = content[content_start : closing.start()]
        block_end = closing.end() + 1 if closing.end() < len(content) else closing.end()
        blocks.append(
            RawDirectiveBlock(raw_content=raw_content, start=opening.start(), end=block_end)
        )
        position = block_end

    return blocks, errors, len(content)


def parse_yaml_embed_blocks(content: str) -> tuple[list[Fragment], list[Status]]:
    """Parse all embedm blocks in markdown content into fragments and errors."""
    if not content:
        return [], []

    raw_blocks, errors, content_end = _find_all_raw_blocks(content)
    fragments: list[Fragment] = []
    position = 0

    for block in raw_blocks:
        text_length = block.start - position
        if text_length > 0:
            fragments.append(Span(position, text_length))

        directive, block_errors = parse_yaml_embed_block(block.raw_content)
        if directive is not None:
            fragments.append(directive)
        errors.extend(block_errors)

        position = block.end

    remaining_length = content_end - position
    if remaining_length > 0:
        fragments.append(Span(position, remaining_length))

    return fragments, errors
