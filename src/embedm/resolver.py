"""Core content resolution logic with embed processing."""

import os
import re
from typing import Optional, Set, Dict

from .parsing import parse_yaml_embed_block
from .registry import dispatch_embed
from .phases import ProcessingPhase


class ProcessingContext:
    """Context for tracking limits during processing."""
    def __init__(self, limits=None, sandbox=None):
        self.limits = limits
        self.sandbox = sandbox
        self.embed_counts = {}  # Track embeds per file
        self.total_embeds = 0

    def increment_embed_count(self, file_path: str) -> Optional[str]:
        """
        Increment embed count for a file and check limits.
        Returns warning message if limit exceeded, None otherwise.
        """
        if self.limits is None or self.limits.max_embeds_per_file <= 0:
            return None

        self.embed_counts[file_path] = self.embed_counts.get(file_path, 0) + 1
        self.total_embeds += 1

        if self.embed_counts[file_path] > self.limits.max_embeds_per_file:
            from .models import Limits
            return f"> [!CAUTION]\n> **Embed Limit Exceeded:** File has {self.embed_counts[file_path]} embeds, limit is {self.limits.max_embeds_per_file}. Use `--max-embeds` to increase this limit."

        return None


def resolve_content(absolute_file_path: str, processing_stack: Optional[Set[str]] = None, context: Optional[ProcessingContext] = None) -> str:
    """
    Recursive Resolver with Path Scoping and Limit Checking

    Args:
        absolute_file_path: Path to the file to process
        processing_stack: Set of files being processed (for cycle detection)
        context: Processing context with limits
    """
    if processing_stack is None:
        processing_stack = set()

    if context is None:
        context = ProcessingContext()

    # Check for circular dependencies
    if absolute_file_path in processing_stack:
        return f"> [!CAUTION]\n> **Embed Error:** Infinite loop detected! `{os.path.basename(absolute_file_path)}` is trying to embed a parent."

    if not os.path.exists(absolute_file_path) or os.path.isdir(absolute_file_path):
        return f"> [!CAUTION]\n> **Embed Error:** File not found: `{absolute_file_path}`"

    # Check recursion depth
    if context.limits and context.limits.max_recursion > 0:
        if len(processing_stack) >= context.limits.max_recursion:
            from .models import Limits
            return f"> [!CAUTION]\n> **Recursion Limit Exceeded:** Maximum recursion depth of {context.limits.max_recursion} reached. Use `--max-recursion` to increase this limit."

    processing_stack.add(absolute_file_path)

    # Check file size limit
    if context.limits and context.limits.max_file_size > 0:
        file_size = os.path.getsize(absolute_file_path)
        if file_size > context.limits.max_file_size:
            from .models import Limits
            return f"> [!CAUTION]\n> **File Size Limit Exceeded:** File size {Limits.format_size(file_size)} exceeds limit {Limits.format_size(context.limits.max_file_size)}. Use `--max-file-size` to increase this limit."

    with open(absolute_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    current_file_dir = os.path.dirname(absolute_file_path)

    # Regex to find ```yaml embedm ... ``` blocks
    yaml_regex = re.compile(r'^```yaml embedm\s*\n([\s\S]*?)```', re.MULTILINE)

    def replace_embed(match):
        yaml_content = match.group(1)

        # Try to parse as YAML embed block
        parsed = parse_yaml_embed_block(yaml_content)

        if not parsed:
            # Not an embed block, leave as-is
            return match.group(0)

        embed_type, properties = parsed

        # Check embed count limit
        limit_warning = context.increment_embed_count(absolute_file_path)
        if limit_warning:
            return limit_warning

        # Route to appropriate handler via plugin dispatcher
        result = dispatch_embed(
            embed_type=embed_type,
            properties=properties,
            current_file_dir=current_file_dir,
            processing_stack=processing_stack,
            context=context,
            phase=ProcessingPhase.EMBED
        )

        # If result is None, it means defer to POST_PROCESS phase (e.g., TOC)
        if result is None:
            return match.group(0)

        return result

    resolved = yaml_regex.sub(replace_embed, content)
    return resolved


def resolve_table_of_contents(content: str, source_file_path: str = None) -> str:
    """
    Post-process to resolve table_of_contents embeds

    Args:
        content: Content with TOC markers to resolve
        source_file_path: Path to the source file (for resolving relative paths in source property)
    """
    import os

    # Regex to find EmbedM YAML blocks
    yaml_regex = re.compile(r'^```yaml embedm\s*\n([\s\S]*?)```', re.MULTILINE)

    # Get directory of source file for resolving relative paths
    current_file_dir = os.path.dirname(os.path.abspath(source_file_path)) if source_file_path else None

    def replace_toc(match):
        yaml_content = match.group(1)
        parsed = parse_yaml_embed_block(yaml_content)

        if not parsed:
            return match.group(0)

        embed_type, properties = parsed

        if embed_type in ('toc', 'table_of_contents'):
            # Try plugin dispatcher first
            result = dispatch_embed(
                embed_type=embed_type,
                properties=properties,
                current_file_dir=current_file_dir,
                processing_stack=set(),  # POST_PROCESS doesn't track cycles
                context=None,
                phase=ProcessingPhase.POST_PROCESS
            )

            # If plugin returns None (no source specified), generate from current content
            if result is None:
                # Import here to avoid circular dependency
                from .converters import generate_table_of_contents

                # Get the position of the TOC embed in the content
                toc_position = match.start()

                # Extract only content AFTER the TOC embed to avoid including:
                # 1. Document title (first H1)
                # 2. "Table of Contents" heading itself
                # 3. Any other headings before the TOC
                content_after_toc = content[match.end():]

                # Remove any remaining TOC embeds from the content after this one
                temp_content = yaml_regex.sub(
                    lambda m: '' if parse_yaml_embed_block(m.group(1)) and
                    parse_yaml_embed_block(m.group(1))[0] in ('toc', 'table_of_contents')
                    else m.group(0),
                    content_after_toc
                )

                # Pass depth property if specified
                depth = properties.get('depth')
                max_depth = int(depth) if depth is not None else None

                return generate_table_of_contents(temp_content, max_depth=max_depth)

            return result
        elif embed_type == 'comment':
            # Remove comments in second pass (in case they weren't caught in first pass)
            return ''

        return match.group(0)

    return yaml_regex.sub(replace_toc, content)
