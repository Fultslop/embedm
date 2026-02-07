"""Core content resolution logic with embed processing."""

import os
import re
from typing import Optional, Set

from .parsing import parse_yaml_embed_block
from .processors import process_file_embed
from .converters import generate_table_of_contents


def resolve_content(absolute_file_path: str, processing_stack: Optional[Set[str]] = None) -> str:
    """
    Recursive Resolver with Path Scoping
    """
    if processing_stack is None:
        processing_stack = set()

    if absolute_file_path in processing_stack:
        return f"> [!CAUTION]\n> **Embed Error:** Infinite loop detected! `{os.path.basename(absolute_file_path)}` is trying to embed a parent."

    if not os.path.exists(absolute_file_path) or os.path.isdir(absolute_file_path):
        return f"> [!CAUTION]\n> **Embed Error:** File not found: `{absolute_file_path}`"

    processing_stack.add(absolute_file_path)

    with open(absolute_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    current_file_dir = os.path.dirname(absolute_file_path)

    # Regex to find ```yaml ... ``` blocks
    yaml_regex = re.compile(r'^```yaml\s*\n([\s\S]*?)```', re.MULTILINE)

    def replace_embed(match):
        yaml_content = match.group(1)

        # Try to parse as YAML embed block
        parsed = parse_yaml_embed_block(yaml_content)

        if not parsed:
            # Not an embed block, leave as-is
            return match.group(0)

        embed_type, properties = parsed

        # Route to appropriate handler based on type
        if embed_type == 'file':
            return process_file_embed(properties, current_file_dir, processing_stack)
        elif embed_type == 'toc' or embed_type == 'table_of_contents':
            # TOC is handled in a second pass, leave marker
            return match.group(0)
        else:
            return f"> [!CAUTION]\n> **Embed Error:** Unknown embed type: `{embed_type}`"

    resolved = yaml_regex.sub(replace_embed, content)
    return resolved


def resolve_table_of_contents(content: str) -> str:
    """
    Post-process to resolve table_of_contents embeds
    """
    # Regex to find YAML blocks
    yaml_regex = re.compile(r'^```yaml\s*\n([\s\S]*?)```', re.MULTILINE)

    def replace_toc(match):
        yaml_content = match.group(1)
        parsed = parse_yaml_embed_block(yaml_content)

        if not parsed:
            return match.group(0)

        embed_type, properties = parsed

        if embed_type in ('toc', 'table_of_contents'):
            # Generate TOC from current content (without TOC markers)
            # First remove all TOC embeds to avoid including them
            temp_content = yaml_regex.sub(lambda m: '' if parse_yaml_embed_block(m.group(1)) and parse_yaml_embed_block(m.group(1))[0] in ('toc', 'table_of_contents') else m.group(0), content)
            return generate_table_of_contents(temp_content)

        return match.group(0)

    return yaml_regex.sub(replace_toc, content)
