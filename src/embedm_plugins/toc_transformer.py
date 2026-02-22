import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from embedm.domain.document import Fragment
from embedm.plugins.transformer_base import TransformerBase
from embedm_plugins.toc_resources import str_resources

MAX_DEPTH_KEY = "max_depth"
ADD_SLUGS_KEY = "add_slugs"
START_FRAGMENT_KEY = "start_fragment"

TOC_OPTION_KEY_TYPES = {START_FRAGMENT_KEY: int, MAX_DEPTH_KEY: int, ADD_SLUGS_KEY: bool}


@dataclass
class ToCParams:
    parent_document: Sequence[Fragment]
    start_fragment: int
    max_depth: int
    add_slugs: bool


class ToCTransformer(TransformerBase[ToCParams]):
    params_type = ToCParams

    def execute(self, params: ToCParams) -> str:
        toc_lines = []
        heading_counts: dict[str, int] = {}  # Track duplicate headings for unique anchors

        for fragment in params.parent_document[params.start_fragment :]:
            if isinstance(fragment, str):
                fragment_content = self._parse_str_fragment(
                    fragment, params.max_depth, heading_counts, params.add_slugs
                )
                if fragment_content:
                    toc_lines.append(fragment_content)

        if toc_lines:
            toc_content = "\n".join(toc_lines)
            return f"{toc_content}\n"

        return f"{str_resources.note_no_toc_content}\n"

    def _parse_str_fragment(
        self,
        content: str,
        max_depth: int,
        heading_counts: dict[str, int],
        add_slugs: bool,
    ) -> str:

        toc_lines = []

        for line in self._iter_visible_lines(content):
            heading = self._extract_heading(line, max_depth)
            if heading is None:
                continue

            level, text = heading
            toc_line = self._build_toc_line(level, text, heading_counts, add_slugs)
            toc_lines.append(toc_line)

        return "\n".join(toc_lines)

    def _iter_visible_lines(self, content: str) -> Iterator[str]:
        lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")

        is_in_fence = False
        fence_marker = ""

        for line in lines:
            is_fence_line, is_in_fence, fence_marker = is_fenced_line(line, is_in_fence, fence_marker)

            if not is_fence_line and not is_in_fence:
                yield line

    def _extract_heading(self, line: str, max_depth: int) -> tuple[int, str] | None:
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if not match:
            return None

        level = len(match.group(1))

        if level > max_depth:
            return None

        return level, match.group(2).strip()

    def _build_toc_line(
        self,
        level: int,
        text: str,
        heading_counts: dict[str, int],
        add_slugs: bool,
    ) -> str:

        slug = slugify(text)

        if slug in heading_counts:
            heading_counts[slug] += 1
            slug = f"{slug}-{heading_counts[slug]}"
        else:
            heading_counts[slug] = 0

        indent = "  " * (level - 1)

        if add_slugs:
            return f"{indent}- [{text}](#{slug})"

        return f"{indent}- {text}"


# Track fenced code blocks so we skip headings inside them
def is_fenced_line(line: str, is_fenced: bool, fence_marker: str) -> tuple[bool, bool, str]:
    stripped = line.strip()

    if stripped.startswith("```"):
        if not is_fenced:
            return True, True, "`" * (len(stripped) - len(stripped.lstrip("`")))
        elif stripped.startswith(fence_marker) and stripped.strip("`").strip() == "":
            return True, False, fence_marker

    return False, is_fenced, fence_marker


def slugify(text: str) -> str:
    """
    Generates a GitHub-style anchor slug from a heading
    """
    result = text.lower().strip()
    result = re.sub(r"[^\w\s-]", "", result)  # Remove special chars
    result = re.sub(r"[\s_]+", "-", result)  # Replace spaces with hyphens
    result = re.sub(r"^-+|-+$", "", result)  # Remove leading/trailing hyphens
    return result
