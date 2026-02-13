"""
Processing Phases in EmbedM
============================

EmbedM uses a multi-phase processing pipeline to transform markdown documents with
embedded content. This module defines the phase system and execution framework.

## Processing Phases

1. **EMBED Phase:**
   - Resolves file embeds (complete files or regions)
   - Converts CSV files to markdown tables
   - Processes layout embeds (multi-column/row arrangements)
   - Handles recursive markdown embeds
   - Removes comment blocks
   - Enforces safety limits (file size, recursion depth, embed counts)

2. **POST_PROCESS Phase:**
   - Generates table of contents (requires complete document state)
   - Final comment cleanup (safety measure)
   - Future: custom transformations, finalization steps

## Architecture

Phases execute in the order they're defined in the ProcessingPhase enum. Each phase
receives the output of the previous phase, enabling a clean separation of concerns.

## Adding New Phases

To add a new processing phase:

1. Add enum member to ProcessingPhase (order determines execution sequence)
2. Add handler method to PhaseProcessor._register_handlers()
3. Implement the handler method in PhaseProcessor

Example:
    ```python
    class ProcessingPhase(Enum):
        EMBED = "embed"
        POST_PROCESS = "post"
        FINALIZE = "finalize"  # NEW

    def _register_handlers(self):
        return {
            ProcessingPhase.EMBED: self._execute_embed_phase,
            ProcessingPhase.POST_PROCESS: self._execute_post_process_phase,
            ProcessingPhase.FINALIZE: self._execute_finalize_phase  # NEW
        }

    def _execute_finalize_phase(self, file_path: str, content: str) -> str:
        # Custom finalization logic
        return content
    ```

## Phase Order

Phase order matters. POST_PROCESS phases require the complete document state after
all embeds are resolved. If you change phase order, ensure dependencies are respected.
"""

from enum import Enum
from typing import Optional


class ProcessingPhase(Enum):
    """Processing phases for embed resolution.

    Phases execute in the order they're defined here.
    """

    EMBED = "embed"           # First pass: resolve file/csv/layout embeds
    POST_PROCESS = "post"     # Second pass: TOC generation, final cleanup

    @property
    def display_name(self) -> str:
        """Human-readable phase name for logging and errors."""
        return {
            ProcessingPhase.EMBED: "Embed Resolution",
            ProcessingPhase.POST_PROCESS: "Post-Processing"
        }[self]


class PhaseProcessor:
    """Executes processing phases in order.

    This class manages the multi-phase processing pipeline, executing each
    phase sequentially and threading content between phases.

    Args:
        context: Optional ProcessingContext for limits and state tracking.
                 If not provided, a default context is created.

    Example:
        ```python
        from embedm.phases import PhaseProcessor
        from embedm.resolver import ProcessingContext

        context = ProcessingContext(limits=my_limits)
        processor = PhaseProcessor(context=context)
        result = processor.process_all_phases("path/to/file.md")
        ```
    """

    def __init__(self, context: Optional['ProcessingContext'] = None):
        """Initialize phase processor.

        Args:
            context: Optional processing context for limits and state tracking
        """
        # Import here to avoid circular dependency
        from .resolver import ProcessingContext

        self.context = context or ProcessingContext()
        self._phase_handlers = self._register_handlers()

    def _register_handlers(self) -> dict:
        """Register handler function for each phase.

        Returns:
            Dictionary mapping ProcessingPhase → handler function
        """
        return {
            ProcessingPhase.EMBED: self._execute_embed_phase,
            ProcessingPhase.POST_PROCESS: self._execute_post_process_phase
        }

    def process_all_phases(self, file_path: str) -> str:
        """Execute all phases in order.

        Phases execute sequentially, with each phase receiving the output
        of the previous phase.

        Args:
            file_path: Absolute path to the markdown file to process

        Returns:
            Processed content after all phases complete

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is a directory
            RecursionError: If recursion depth exceeded
            Other errors from individual phase handlers
        """
        content = None

        # Execute phases in enum definition order
        for phase in ProcessingPhase:
            handler = self._phase_handlers[phase]
            content = handler(file_path, content)

        return content

    def _execute_embed_phase(self, file_path: str, content: Optional[str]) -> str:
        """Phase 1: Resolve embeds.

        Processes all embed directives (file, csv, layout, comment) and handles
        recursive markdown embeds.

        Args:
            file_path: Path to file being processed
            content: Unused in this phase (always reads from file)

        Returns:
            Content with all embeds resolved
        """
        # Import here to avoid circular dependency
        from .resolver import resolve_content

        return resolve_content(file_path, context=self.context)

    def _execute_post_process_phase(self, file_path: str, content: str) -> str:
        """Phase 2: Post-processing (TOC generation).

        Generates table of contents from the resolved document content.
        Requires complete document state from EMBED phase.

        Args:
            file_path: Path to file being processed (for reference)
            content: Content from EMBED phase

        Returns:
            Content with TOC generated and final cleanup applied
        """
        # Import here to avoid circular dependency
        from .resolver import resolve_table_of_contents

        return resolve_table_of_contents(content, source_file_path=file_path)
