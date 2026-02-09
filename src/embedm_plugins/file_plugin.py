"""
File Plugin for EmbedM
=======================

Handles file and code embeds, including:
- Complete file embedding
- Line range selection (10-20)
- Named region extraction (md.start:name / md.end:name)
- Line number display (text or HTML)

Usage in markdown:
    ```yaml embedm
    type: file
    source: path/to/file.py
    lines: 10-20  # Optional
    line_numbers: html  # Optional: text, html, table, or omit
    title: My Code  # Optional
    ```
"""

import os
from typing import Dict, Set, Optional, List

# Import from embedm core
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext, resolve_content
from embedm.extraction import extract_lines, extract_region
from embedm.formatting import (
    format_with_line_numbers,
    format_with_line_numbers_text,
    format_with_line_numbers_table,
    dedent_lines
)


class FilePlugin(EmbedPlugin):
    """Plugin that handles file and code embeds.

    Handles embed types:
    - embed.file: File embedding with optional line numbers and regions
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "file"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["file"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        """Processing phases when this plugin runs."""
        return [ProcessingPhase.EMBED]

    @property
    def valid_properties(self) -> List[str]:
        """Valid properties for file embeds."""
        return [
            "source",              # Required: file path
            "title",               # Optional: title for the embed
            "lines",               # Optional: line range (e.g., "10-20", "15", "10-")
            "region",              # Optional: named region to extract
            "line_numbers",        # Optional: "text" or "html"
            "line_numbers_style",  # Optional: style for HTML line numbers
        ]

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        """Process file embed.

        Args:
            properties: YAML properties (source, region, line_numbers, title)
            current_file_dir: Directory containing the markdown file
            processing_stack: Set of files being processed (cycle detection)
            context: Processing context with limits

        Returns:
            Embedded file content or error message
        """
        if context is None:
            context = ProcessingContext()

        source = properties.get('source')
        if not source:
            return "> [!CAUTION]\n> **Embed Error:** 'source' property is required for file embeds"

        lines = properties.get('lines')  # Line range (e.g., "L4-6")
        region = properties.get('region')  # Named region
        title = properties.get('title')
        line_numbers = properties.get('line_numbers', False)
        line_numbers_style = properties.get('line_numbers_style', 'default')

        # Normalize line_numbers value
        if isinstance(line_numbers, str):
            line_numbers = line_numbers.lower()
            if line_numbers not in ('text', 'html', 'table', 'false'):
                line_numbers = 'html' if line_numbers in ('true', 'yes', '1') else False
        elif isinstance(line_numbers, bool):
            line_numbers = 'html' if line_numbers else False
        else:
            line_numbers = False

        target_path = os.path.abspath(os.path.join(current_file_dir, source))
        is_markdown = target_path.endswith('.md')

        if not os.path.exists(target_path):
            return f"> [!CAUTION]\n> **Embed Error:** File not found: `{source}`"

        # Check file size limit
        if context.limits and context.limits.max_file_size > 0:
            file_size = os.path.getsize(target_path)
            if file_size > context.limits.max_file_size:
                from embedm.models import Limits
                return f"> [!CAUTION]\n> **File Size Limit Exceeded:** Source file `{os.path.basename(target_path)}` size {Limits.format_size(file_size)} exceeds limit {Limits.format_size(context.limits.max_file_size)}. Use `--max-file-size` to increase this limit."

        with open(target_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Case A: Embedding specific part (lines/region) or non-Markdown file
        if lines or region or not is_markdown:
            result_data = None
            ext = os.path.splitext(target_path)[1][1:] or 'text'

            # Extract specific lines or region
            if lines:
                # Extract line range (e.g., "L4-6")
                result_data = extract_lines(raw_content, lines)
                if not result_data:
                    return f"> [!CAUTION]\n> Invalid line range `{lines}` in `{source}`"
            elif region:
                # Try L10-20 format first (for backward compatibility)
                result_data = extract_lines(raw_content, region)
                # If not L-format, try named region tags
                if not result_data:
                    result_data = extract_region(raw_content, region)

                if not result_data:
                    return f"> [!CAUTION]\n> Region `{region}` not found in `{source}`"

            # Apply line numbers if we extracted specific lines/region
            if result_data:
                if line_numbers == 'html':
                    raw_content = format_with_line_numbers(
                        result_data['lines'],
                        result_data['startLine'],
                        ext,
                        line_numbers_style,
                        current_file_dir
                    )
                elif line_numbers == 'text':
                    raw_content = format_with_line_numbers_text(
                        result_data['lines'],
                        result_data['startLine']
                    )
                elif line_numbers == 'table':
                    raw_content = format_with_line_numbers_table(
                        result_data['lines'],
                        result_data['startLine'],
                        ext
                    )
                else:
                    # Just dedent the lines without numbers
                    raw_content = dedent_lines(result_data['lines'])
            else:
                # Whole file without region - apply line numbers if requested
                if line_numbers:
                    lines = raw_content.split('\n')
                    if line_numbers == 'html':
                        raw_content = format_with_line_numbers(
                            lines,
                            1,
                            ext,
                            line_numbers_style,
                            current_file_dir
                        )
                    elif line_numbers == 'text':
                        raw_content = format_with_line_numbers_text(lines, 1)
                    elif line_numbers == 'table':
                        raw_content = format_with_line_numbers_table(lines, 1, ext)

            # Check embedded text size limit
            if context.limits and context.limits.max_embed_text > 0:
                text_size = len(raw_content.encode('utf-8'))
                if text_size > context.limits.max_embed_text:
                    from embedm.models import Limits
                    return f"> [!CAUTION]\n> **Embed Text Limit Exceeded:** Embedded content size {Limits.format_size(text_size)} exceeds limit {Limits.format_size(context.limits.max_embed_text)}. Use `--max-embed-text` to increase this limit."

            # Build result with optional title
            result = ''
            if title:
                result += f"**{title}**\n\n"

            # If we formatted with HTML or table line numbers, return as-is (no code block wrapper)
            if line_numbers in ('html', 'table'):
                result += raw_content
            else:
                # Standard markdown code block (for text line numbers or no line numbers)
                result += f"```{ext}\n{raw_content.rstrip()}\n```"

            return result

        # Case B: Embedding another Markdown file recursively
        embedded_md = resolve_content(target_path, set(processing_stack), context)

        # Add title if specified
        if title:
            return f"**{title}**\n\n{embedded_md}"

        return embedded_md
