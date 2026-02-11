"""
TOC Plugin for EmbedM
=====================

Handles table of contents generation from markdown headings.

Usage in markdown:
    ```yaml embedm
    type: toc
    source: document.md  # Optional: generate TOC from specific file
    ```

Note: TOC generation from current document content requires special handling
in the POST_PROCESS phase and is not yet fully supported through the plugin
interface. This plugin currently handles TOC generation from external files.
"""

import os
import re
from typing import Dict, Set, Optional, List

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext
from embedm.converters import slugify


class TOCPlugin(EmbedPlugin):
    """Plugin that handles table of contents generation.

    Handles embed types:
    - embed.toc: Table of contents generation
    - embed.table_of_contents: Legacy alias
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "toc"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["toc", "table_of_contents"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        """Processing phases when this plugin runs."""
        return [ProcessingPhase.POST_PROCESS]

    @property
    def valid_properties(self) -> List[str]:
        """Valid properties for TOC embeds."""
        return [
            "source",  # Optional: file to generate TOC from
            "depth",   # Optional: max heading depth to include (e.g., 2 = # and ## only)
        ]

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        """Process TOC embed.

        Args:
            properties: YAML properties (source, etc.)
            current_file_dir: Directory containing the markdown file
            processing_stack: Set of files being processed (cycle detection)
            context: Processing context with limits

        Returns:
            Generated table of contents or error message

        Note:
            Currently only supports TOC generation from external files via
            'source' property. TOC generation from current document content
            requires special handling and is deferred to POST_PROCESS phase
            handler.
        """
        # Check if source file is specified
        source = properties.get('source')

        depth = properties.get('depth')
        max_depth = int(depth) if depth is not None else None

        if source:
            # Generate TOC from specified file
            target_path = os.path.abspath(os.path.join(current_file_dir, source))

            if not os.path.exists(target_path):
                return f"> [!CAUTION]\n> **TOC Error:** Source file not found: `{source}`"

            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return f"> [!CAUTION]\n> **TOC Error:** Could not read `{source}`: {str(e)}"

            return self._generate_toc(content, max_depth=max_depth)
        else:
            # This case requires full document content which isn't available
            # in the plugin interface yet. Return None to signal that this
            # should be handled by the POST_PROCESS phase handler.
            return None

    def _generate_toc(self, content: str, max_depth: int = None) -> str:
        """Generate table of contents from markdown content.

        Args:
            content: Markdown content to parse for headings
            max_depth: Maximum heading depth to include (e.g., 2 = # and ## only).
                       None means no limit.

        Returns:
            Generated table of contents as markdown list
        """
        # Normalize line endings first
        lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        toc_lines = []
        heading_counts = {}  # Track duplicate headings for unique anchors

        for line in lines:
            # Match markdown headings (# through ######)
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
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
            indent = '  ' * (level - 1)

            # Add to TOC
            toc_lines.append(f"{indent}- [{text}](#{slug})")

        return '\n'.join(toc_lines) if toc_lines else '> [!NOTE]\n> No headings found in document.'
