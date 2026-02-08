"""
File Plugin for EmbedM
=======================

Handles file and code embeds, including:
- Complete file embedding
- Line range selection (L10-20)
- Named region extraction (md.start:name / md.end:name)
- Line number display (text or HTML)
- CSV to table conversion

Usage in markdown:
    ```yaml
    type: embed.file
    source: path/to/file.py
    region: L10-20  # Optional
    line_numbers: html  # Optional: text, html, or omit
    title: My Code  # Optional
    ```
"""

from typing import Dict, Set, Optional, List

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext


class FilePlugin(EmbedPlugin):
    """Plugin that handles file and code embeds.

    This plugin wraps the existing process_file_embed() function from
    embedm.processors. It provides backward compatibility while enabling
    the plugin architecture.

    Handles embed types:
    - embed.file: Standard file embedding
    - embed.embed: Legacy alias for file embedding
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "file"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["file", "embed"]  # 'embed' is legacy alias

    @property
    def phases(self) -> List[ProcessingPhase]:
        """Processing phases when this plugin runs."""
        return [ProcessingPhase.EMBED]

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        """Process file embed by delegating to existing handler.

        Args:
            properties: YAML properties (source, region, line_numbers, title)
            current_file_dir: Directory containing the markdown file
            processing_stack: Set of files being processed (cycle detection)
            context: Processing context with limits

        Returns:
            Embedded file content or error message
        """
        # Import the existing handler
        from embedm.processors import process_file_embed

        # Delegate to the existing implementation
        return process_file_embed(
            properties,
            current_file_dir,
            processing_stack,
            context
        )
