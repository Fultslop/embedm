"""
Table Plugin for EmbedM
========================

Handles embedding tabular data as markdown tables.

Currently supports:
- CSV files
- JSON files (arrays of objects)

Future support planned for:
- TSV files
- Excel files

Usage in markdown:
    ```yaml
    type: embed.table
    source: data/users.csv
    title: User List  # Optional
    ```

    ```yaml
    type: embed.table
    source: data/users.json
    columns: [name, email, role]  # Optional: select specific columns
    ```
"""

import os
import json
from typing import Dict, Set, Optional, List, Any

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext
from embedm.converters import csv_to_markdown_table


class TablePlugin(EmbedPlugin):
    """Plugin that handles table embeds from CSV, JSON, and other tabular formats.

    Handles embed types:
    - embed.table: Convert CSV/JSON/TSV/etc. to markdown tables
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
        elif ext == 'json':
            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                return f"> [!CAUTION]\n> **Table Error:** Invalid JSON in `{source}`: {str(e)}"

            # Get optional column selection
            columns = properties.get('columns')

            # Convert JSON to table
            table = self._json_to_markdown_table(data, columns)
            if table.startswith("> [!CAUTION]"):
                return table  # Error message
        elif ext == 'tsv':
            # TSV support - future enhancement
            return f"> [!CAUTION]\n> **Table Error:** TSV format not yet supported. Use CSV or JSON for now."
        else:
            return f"> [!CAUTION]\n> **Table Error:** Unsupported file format `.{ext}`. Currently CSV and JSON are supported."

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

    def _json_to_markdown_table(self, data: Any, columns: Optional[List[str]] = None) -> str:
        """Convert JSON data to markdown table.

        Args:
            data: Parsed JSON data (array of objects, single object, or dict)
            columns: Optional list of column names to include (in order)

        Returns:
            Markdown table string or error message
        """
        # Case 1: Array of objects (most common)
        if isinstance(data, list):
            if not data:
                return "> [!CAUTION]\n> **Table Error:** JSON array is empty"

            # Check if all items are objects
            if not all(isinstance(item, dict) for item in data):
                return "> [!CAUTION]\n> **Table Error:** JSON array must contain objects for table conversion"

            # Determine columns
            if columns:
                # Use specified columns
                cols = columns
            else:
                # Use keys from first object
                cols = list(data[0].keys())

            # Build table header
            lines = ['| ' + ' | '.join(cols) + ' |']
            lines.append('| ' + ' | '.join(['---'] * len(cols)) + ' |')

            # Build table rows
            for item in data:
                row = []
                for col in cols:
                    value = item.get(col, '')
                    # Convert value to string and escape pipes
                    if isinstance(value, bool):
                        value_str = 'true' if value else 'false'
                    elif value is None:
                        value_str = ''
                    else:
                        value_str = str(value)
                    value_str = value_str.replace('|', '\\|').replace('\n', ' ')
                    row.append(value_str)
                lines.append('| ' + ' | '.join(row) + ' |')

            return '\n'.join(lines)

        # Case 2: Single object (convert to key-value table)
        elif isinstance(data, dict):
            lines = ['| Key | Value |']
            lines.append('| --- | --- |')
            for key, value in data.items():
                # Convert value to string and escape pipes
                if isinstance(value, bool):
                    value_str = 'true' if value else 'false'
                elif value is None:
                    value_str = ''
                elif isinstance(value, (list, dict)):
                    value_str = json.dumps(value)
                else:
                    value_str = str(value)
                value_str = value_str.replace('|', '\\|').replace('\n', ' ')
                lines.append(f'| {key} | {value_str} |')
            return '\n'.join(lines)

        # Case 3: Other types not supported
        else:
            return f"> [!CAUTION]\n> **Table Error:** JSON must be an array of objects or a single object for table conversion, got {type(data).__name__}"
