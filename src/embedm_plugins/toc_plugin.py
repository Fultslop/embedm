"""
TOC Plugin for EmbedM
=====================

Handles table of contents generation from markdown headings.

Usage in markdown:
    ```yaml
    type: embed.toc
    source: document.md  # Optional: generate TOC from specific file
    ```

Note: TOC generation from current document content requires special handling
in the POST_PROCESS phase and is not yet fully supported through the plugin
interface. This plugin currently handles TOC generation from external files.
"""

from typing import Dict, Set, Optional, List

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext


class TOCPlugin(EmbedPlugin):
    """Plugin that handles table of contents generation.

    This plugin wraps the existing generate_table_of_contents() function
    from embedm.converters. Currently supports TOC generation from external
    files specified via 'source' property.

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
        # Import the existing handler
        from embedm.converters import generate_table_of_contents

        # Check if source file is specified
        source = properties.get('source')

        if source:
            # Generate TOC from specified file
            return generate_table_of_contents(
                '',
                source_file=source,
                current_file_dir=current_file_dir
            )
        else:
            # This case requires full document content which isn't available
            # in the plugin interface yet. Return None to signal that this
            # should be handled by the POST_PROCESS phase handler.
            return None
