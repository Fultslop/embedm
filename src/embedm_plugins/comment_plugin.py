"""
Comment Plugin for EmbedM
===========================

Handles comment embeds that should be removed from the output.

Comments are used for documentation within markdown source files but
are not included in the processed output.

Usage in markdown:
    ```yaml embedm
    type: comment
    content: This is a note to myself that won't appear in the output
    ```
"""

from typing import Dict, Set, Optional, List

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext


class CommentPlugin(EmbedPlugin):
    """Plugin that handles comment embeds.

    Comments are removed from the output entirely. They can be used for:
    - Documentation notes in source files
    - Temporary markers during editing
    - Explanatory text that shouldn't appear in final output

    Handles embed types:
    - embed.comment: Comment blocks that are removed from output
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "comment"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["comment"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        """Phases when this plugin executes."""
        # Run in both phases to ensure comments are always removed
        return [ProcessingPhase.EMBED, ProcessingPhase.POST_PROCESS]

    @property
    def valid_properties(self) -> List[str]:
        """Valid properties for comment embeds."""
        return ["content", "note", "text"]  # All optional, just for documentation

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        """Process comment embed by removing it.

        Args:
            properties: YAML properties (ignored)
            current_file_dir: Directory of markdown file (ignored)
            processing_stack: Processing stack for cycle detection (ignored)
            context: Processing context (ignored)

        Returns:
            Empty string (comments are removed from output)
        """
        # Comments are always removed - return empty string
        return ""
