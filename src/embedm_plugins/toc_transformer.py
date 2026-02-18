import re
from collections.abc import Sequence
from dataclasses import dataclass

from embedm.domain.document import Fragment
from embedm.plugins.transformer_base import TransformerBase
from embedm_plugins.plugin_resources import str_resources

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

        for _index, fragment in enumerate(params.parent_document[params.start_fragment :]):
            if isinstance(fragment, str):
                toc_lines.append(self._parse_str_fragment(fragment, params.max_depth, heading_counts, params.add_slugs))

        return "\n".join(toc_lines) + "\n" if toc_lines else str_resources.note_no_toc_content

    def _parse_str_fragment(self, content: str, max_depth: int, heading_counts: dict[str, int], add_slugs: bool) -> str:
        # Normalize line endings first
        lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        toc_lines = []

        is_in_fence = False
        fence_marker = ""

        for line in lines:
            is_fence_line, is_in_fence, fence_marker = is_fenced_line(line, is_in_fence, fence_marker)

            if not is_fence_line and not is_in_fence:
                # Match markdown headings (# through ######)
                match = re.match(r"^(#{1,6})\s+(.+)$", line)
                if not match:
                    continue

                level = len(match.group(1))

                # Skip headings deeper than max_depth
                if max_depth is not None and level > max_depth:
                    continue
                text = match.group(2).strip()

                # Generate slug (GitHub style)
                slug = slugify(text)

                # Handle duplicate headings by appending -1, -2, etc.
                if slug in heading_counts:
                    heading_counts[slug] += 1
                    slug = f"{slug}-{heading_counts[slug]}"
                else:
                    heading_counts[slug] = 0

                # Create indentation (2 spaces per level beyond h1)
                indent = "  " * (level - 1)

                # Add to TOC
                if add_slugs:
                    toc_lines.append(f"{indent}- [{text}](#{slug})")
                else:
                    toc_lines.append(f"{indent}- {text}")

        return "\n".join(toc_lines) if toc_lines else str_resources.note_no_toc_content


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
