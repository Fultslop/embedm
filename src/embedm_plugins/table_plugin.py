"""
Table Plugin for EmbedM
========================

Handles embedding tabular data as markdown tables.

Currently supports:
- CSV files

Future support planned for:
- TSV files
- Excel files
- JSON arrays

Usage in markdown:
    ```yaml
    type: embed.table
    source: data/users.csv
    title: User List  # Optional
    ```
"""

import os
from typing import Dict, Set, Optional, List

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext
from embedm.converters import csv_to_markdown_table


class TablePlugin(EmbedPlugin):
    """Plugin that handles table embeds from CSV and other tabular formats.

    Handles embed types:
    - embed.table: Convert CSV/TSV/etc. to markdown tables
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "table"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["table"]

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
        """Process table embed.

        Args:
            properties: YAML properties (source, title, format)
            current_file_dir: Directory containing the markdown file
            processing_stack: Set of files being processed (cycle detection)
            context: Processing context with limits

        Returns:
            Markdown table or error message
        """
        if context is None:
            context = ProcessingContext()

        source = properties.get('source')
        if not source:
            return "> [!CAUTION]\n> **Table Error:** 'source' property is required for table embeds"

        title = properties.get('title')

        # Resolve path
        target_path = os.path.abspath(os.path.join(current_file_dir, source))

        # Check file exists
        if not os.path.exists(target_path):
            return f"> [!CAUTION]\n> **Table Error:** File not found: `{source}`"

        if os.path.isdir(target_path):
            return f"> [!CAUTION]\n> **Table Error:** `{source}` is a directory, not a file"

        # Check file size limit
        if context.limits and context.limits.max_file_size > 0:
            file_size = os.path.getsize(target_path)
            if file_size > context.limits.max_file_size:
                from embedm.models import Limits
                return f"> [!CAUTION]\n> **File Size Limit Exceeded:** Source file `{os.path.basename(target_path)}` size {Limits.format_size(file_size)} exceeds limit {Limits.format_size(context.limits.max_file_size)}. Use `--max-file-size` to increase this limit."

        # Determine file format
        ext = os.path.splitext(target_path)[1][1:].lower()

        # Read file content
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"> [!CAUTION]\n> **Table Error:** Could not read `{source}`: {str(e)}"

        # Convert to markdown table based on format
        if ext == 'csv':
            table = csv_to_markdown_table(content)
        elif ext == 'tsv':
            # TSV support - future enhancement
            return f"> [!CAUTION]\n> **Table Error:** TSV format not yet supported. Use CSV for now."
        else:
            return f"> [!CAUTION]\n> **Table Error:** Unsupported file format `.{ext}`. Currently only CSV is supported."

        # Check embedded table size limit
        if context.limits and context.limits.max_embed_text > 0:
            table_size = len(table.encode('utf-8'))
            if table_size > context.limits.max_embed_text:
                from embedm.models import Limits
                return f"> [!CAUTION]\n> **Embed Text Limit Exceeded:** Table size {Limits.format_size(table_size)} exceeds limit {Limits.format_size(context.limits.max_embed_text)}. Use `--max-embed-text` to increase this limit."

        # Wrap in optional title
        if title:
            return f"**{title}**\n\n{table}"

        return table
