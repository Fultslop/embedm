"""
Plugin System for EmbedM
========================

This module defines the plugin interface for creating custom embed handlers.

## What is a Plugin?

A plugin is a Python class that handles a specific type of embed (file, TOC, CSV, etc.).
Plugins inherit from `EmbedPlugin` and implement the required methods.

## Creating a Plugin

```python
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase

class MyCustomPlugin(EmbedPlugin):
    @property
    def name(self) -> str:
        return "custom"

    @property
    def embed_types(self) -> List[str]:
        return ["custom"]  # Handles type: custom

    @property
    def phases(self) -> List[ProcessingPhase]:
        return [ProcessingPhase.EMBED]

    @property
    def valid_properties(self) -> List[str]:
        return ["source", "title"]

    def process(self, properties, current_file_dir, processing_stack, context):
        # Your implementation here
        source = properties.get('source')
        if not source:
            return self.format_error("Missing Property", "source is required")

        file_path = self.resolve_path(source, current_file_dir)
        error = self.check_file_exists(file_path)
        if error:
            return error

        # Process file and return content
        with open(file_path, 'r') as f:
            content = f.read()

        return self.wrap_in_code_block(content, file_path=file_path)
```

## Plugin Lifecycle

1. **Discovery Phase:** Plugin validates properties (optional validate() method)
2. **Processing Phase:** Plugin processes embed (required process() method)
3. **Error Handling:** Plugin returns error strings, not exceptions

## Utility Methods

- `resolve_path()` - Convert relative to absolute paths
- `format_error()` - Standard error message formatting
- `check_file_exists()` - File existence validation
- `check_limit()` - Limit checking with formatted errors
- `get_file_extension()` - Extract file extension
- `wrap_in_code_block()` - Wrap content in markdown code fence
- `wrap_with_title()` - Add optional title prefix

## Phase Assignment

- **EMBED Phase:** File embeds, CSV conversion, layouts (runs first)
- **POST_PROCESS Phase:** TOC generation (needs complete document)
- **Multi-Phase Plugins:** Return list with multiple phases for cleanup operations

Example multi-phase plugin (comment removal):
```python
@property
def phases(self) -> List[ProcessingPhase]:
    # Runs in both phases for thorough cleanup
    return [ProcessingPhase.EMBED, ProcessingPhase.POST_PROCESS]
```
"""

from abc import ABC, abstractmethod
from typing import Dict, Set, Optional, List, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from .resolver import ProcessingContext
    from .models import ValidationError
    from .phases import ProcessingPhase


class EmbedPlugin(ABC):
    """Abstract base class for embed plugins.

    Plugins handle specific embed types (file, csv, layout, toc, etc.) and
    participate in both validation and processing phases.

    Example:
        ```python
        class FilePlugin(EmbedPlugin):
            @property
            def name(self) -> str:
                return "file"

            @property
            def embed_types(self) -> List[str]:
                return ["file"]

            @property
            def phases(self) -> List[ProcessingPhase]:
                return [ProcessingPhase.EMBED]

            @property
            def valid_properties(self) -> List[str]:
                return ["source", "title", "lines", "region", "line_numbers"]

            def process(self, properties, current_file_dir, processing_stack, context):
                # Implementation here
                return embedded_content
        ```
    """

    # === REQUIRED: Plugin Metadata ===

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier (e.g., 'file', 'toc', 'csv')."""
        pass

    @property
    @abstractmethod
    def embed_types(self) -> List[str]:
        """List of embed type strings this plugin handles.

        Example: ['file'] handles 'type: file' in yaml embedm blocks
        """
        pass

    @property
    @abstractmethod
    def phases(self) -> List['ProcessingPhase']:
        """Processing phases when this plugin executes.

        A plugin can run in multiple phases if needed (e.g., comment removal
        runs in both EMBED and POST_PROCESS for cleanup).

        Returns:
            List of ProcessingPhase values (e.g., [ProcessingPhase.EMBED])
            or [ProcessingPhase.EMBED, ProcessingPhase.POST_PROCESS] for multi-phase
        """
        pass

    @property
    @abstractmethod
    def valid_properties(self) -> List[str]:
        """List of valid property names for this plugin.

        The 'type' and 'comment' properties are always valid and handled
        separately - don't include them in this list.

        Example:
            return ["source", "title", "lines", "region", "line_numbers"]

        Returns:
            List of valid property names (strings)
        """
        pass

    # === REQUIRED: Core Processing ===

    @abstractmethod
    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional['ProcessingContext'] = None
    ) -> str:
        """Process the embed and return content.

        Args:
            properties: Parsed YAML properties (source, title, etc.)
            current_file_dir: Absolute directory of the Markdown file containing the embed
            processing_stack: Set of files currently being processed (for cycle detection)
            context: Processing context with limits and state tracking

        Returns:
            Processed content as string (Markdown or HTML)
            Error message in format: "> [!CAUTION]\n> **Error:** Message"
        """
        pass

    # === OPTIONAL: Validation ===

    def validate(
        self,
        properties: Dict,
        current_file_dir: str,
        file_path: str,
        line_number: int
    ) -> List['ValidationError']:
        """Validate embed properties during discovery phase.

        Override this to add custom validation logic beyond standard checks.

        Args:
            properties: Parsed YAML properties
            current_file_dir: Directory of file containing embed
            file_path: Path to file being validated
            line_number: Line number where embed starts

        Returns:
            List of ValidationError objects (empty if valid)
        """
        return []

    # === UTILITY METHODS ===

    def resolve_path(self, source: str, current_file_dir: str) -> str:
        """Resolve relative path to absolute path.

        Args:
            source: Source path (may be relative)
            current_file_dir: Base directory for relative paths

        Returns:
            Absolute path
        """
        return os.path.abspath(os.path.join(current_file_dir, source))

    def format_error(self, category: str, message: str) -> str:
        """Format error message in standard style.

        Args:
            category: Error category (e.g., "File Not Found", "Limit Exceeded")
            message: Error message

        Returns:
            Formatted error block
        """
        return f"> [!CAUTION]\n> **{category}:** {message}"

    def check_file_exists(self, file_path: str) -> Optional[str]:
        """Check if file exists, return error if not.

        Args:
            file_path: Path to check

        Returns:
            None if file exists, error string if not
        """
        if not os.path.exists(file_path):
            return self.format_error("File Not Found", f"`{file_path}`")
        if os.path.isdir(file_path):
            return self.format_error("Invalid File", f"`{file_path}` is a directory")
        return None

    def check_limit(
        self,
        value: int,
        limit: int,
        category: str,
        value_desc: str,
        limit_desc: str
    ) -> Optional[str]:
        """Check if value exceeds limit, return error if so.

        Args:
            value: Current value to check
            limit: Maximum allowed value
            category: Error category
            value_desc: Description of current value (formatted)
            limit_desc: Description of limit (formatted)

        Returns:
            None if within limit, error string if exceeded
        """
        if limit > 0 and value > limit:
            return self.format_error(
                f"{category} Limit Exceeded",
                f"{value_desc} exceeds limit {limit_desc}"
            )
        return None


# === HELPER FUNCTIONS ===

def get_file_extension(file_path: str) -> str:
    """Get file extension without dot.

    Args:
        file_path: Path to file

    Returns:
        Extension (e.g., 'py', 'md', 'txt') or 'text' if none
    """
    ext = os.path.splitext(file_path)[1][1:]
    return ext if ext else 'text'


def wrap_in_code_block(content: str, language: str = None, file_path: str = None) -> str:
    """Wrap content in markdown code block.

    Args:
        content: Content to wrap
        language: Language identifier (optional, auto-detected from file_path if not provided)
        file_path: File path for language detection (optional)

    Returns:
        Markdown code block
    """
    if language is None and file_path:
        language = get_file_extension(file_path)

    lang = language or 'text'
    return f"```{lang}\n{content.rstrip()}\n```"


def wrap_with_title(content: str, title: str) -> str:
    """Wrap content with optional title.

    Args:
        content: Content to wrap
        title: Title text (if provided)

    Returns:
        Content with title prefix if title provided, otherwise just content
    """
    if title:
        return f"**{title}**\n\n{content}"
    return content
