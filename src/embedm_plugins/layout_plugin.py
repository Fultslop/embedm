"""
Layout Plugin for EmbedM
=========================

Handles layout embeds for creating multi-column/row arrangements with
flexbox-based positioning and styling.

Usage in markdown:
    ```yaml
    type: embed.layout
    rows:
      - columns:
          - embed:
              type: embed.file
              source: file1.py
          - embed:
              type: embed.file
              source: file2.py
        gap: 20px
    ```
"""

from typing import Dict, Set, Optional, List

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext


class LayoutPlugin(EmbedPlugin):
    """Plugin that handles layout embeds.

    This plugin wraps the existing process_layout_embed() function from
    embedm.layout. It provides backward compatibility while enabling
    the plugin architecture.

    Handles embed types:
    - embed.layout: Multi-column/row layouts with flexbox
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "layout"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["layout"]

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
        """Process layout embed by delegating to existing handler.

        Args:
            properties: YAML properties (rows, columns, gap, etc.)
            current_file_dir: Directory containing the markdown file
            processing_stack: Set of files being processed (cycle detection)
            context: Processing context with limits

        Returns:
            HTML layout structure or error message
        """
        # Import the existing handler
        from embedm.layout import process_layout_embed

        # Delegate to the existing implementation
        return process_layout_embed(
            properties,
            current_file_dir,
            processing_stack,
            context
        )
