"""embedm - Markdown file embedding and processing tool."""

from .resolver import resolve_content, resolve_table_of_contents
from .parsing import parse_yaml_embed_block
from .extraction import extract_region, extract_lines
from .formatting import format_with_line_numbers, format_with_line_numbers_text, dedent_lines
from .converters import csv_to_markdown_table, slugify, generate_table_of_contents
from .processors import process_file_embed
from .models import Limits, ValidationError, ValidationResult, EmbedDirective, ProcessingStats
from .discovery import discover_files, discover_embeds_in_file, discover_all_embeds, build_dependency_graph
from .validation import validate_all

__version__ = '0.4.0'

__all__ = [
    # Core resolution functions
    'resolve_content',
    'resolve_table_of_contents',

    # Parsing
    'parse_yaml_embed_block',

    # Extraction
    'extract_region',
    'extract_lines',

    # Formatting
    'format_with_line_numbers',
    'format_with_line_numbers_text',
    'dedent_lines',

    # Converters
    'csv_to_markdown_table',
    'slugify',
    'generate_table_of_contents',

    # Processors
    'process_file_embed',

    # Models
    'Limits',
    'ValidationError',
    'ValidationResult',
    'EmbedDirective',
    'ProcessingStats',

    # Discovery
    'discover_files',
    'discover_embeds_in_file',
    'discover_all_embeds',
    'build_dependency_graph',

    # Validation
    'validate_all',
]
