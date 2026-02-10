"""
Symbol Extraction for EmbedM
=============================

Extracts code symbols (functions, classes, methods, CTEs, etc.) from source
files using regex-based symbol matching and structural block extraction.

Architecture (bottom to top):
1. String/comment state machine - skips literals when counting delimiters
2. Block extraction strategies - brace, paren, indent, keyword
3. Declarative language configs - per-language symbol patterns
4. Public API - extract_symbol() entry point

Adding a new language requires only a new LanguageConfig entry.
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable, Tuple


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SymbolPattern:
    """A pattern for matching a type of symbol in a language.

    Attributes:
        kind: Human-readable label (e.g., 'function', 'class', 'cte')
        regex_template: Regex with {name} placeholder for the symbol name.
        block_style: One of 'brace', 'paren', 'indent', 'keyword'
        keyword_end: For 'keyword' style - closing keyword regex (e.g., r'\\bEND\\b')
        nestable: Whether this symbol can contain nested symbols (for dot notation)
    """
    kind: str
    regex_template: str
    block_style: str
    keyword_end: Optional[str] = None
    nestable: bool = True


@dataclass
class CommentStyle:
    """Defines how a language handles comments and strings.

    Attributes:
        line_comment: Line comment prefix (e.g., '#', '//')
        block_comment_start: Block comment opening (e.g., '/*')
        block_comment_end: Block comment closing (e.g., '*/')
        string_delimiters: String delimiter characters
        triple_quote: Whether triple-quoted strings are supported (Python)
    """
    line_comment: Optional[str] = None
    block_comment_start: Optional[str] = None
    block_comment_end: Optional[str] = None
    string_delimiters: List[str] = field(default_factory=lambda: ['"', "'"])
    triple_quote: bool = False


@dataclass
class LanguageConfig:
    """Complete language definition for symbol extraction.

    Attributes:
        name: Language name (for error messages)
        extensions: File extensions this config handles (without dot)
        comment_style: How comments and strings work
        patterns: Ordered list of SymbolPatterns to try
    """
    name: str
    extensions: List[str]
    comment_style: CommentStyle
    patterns: List[SymbolPattern]


@dataclass
class ScanState:
    """Tracks state while scanning code for delimiters.

    Persists across lines for block comments and multi-line strings.
    """
    in_block_comment: bool = False
    in_string: bool = False
    string_char: Optional[str] = None
    in_triple_quote: bool = False


# =============================================================================
# String/Comment State Machine
# =============================================================================

def scan_line(
    line: str,
    state: ScanState,
    comment_style: CommentStyle,
    callback: Callable[[str, int], None]
) -> ScanState:
    """Scan a line, calling callback only for non-string/non-comment characters.

    Args:
        line: Source line to scan
        state: Current scan state (mutated in place)
        comment_style: Language comment/string rules
        callback: Called with (character, position) for real code chars

    Returns:
        Updated ScanState
    """
    i = 0
    length = len(line)

    while i < length:
        # --- Inside block comment ---
        if state.in_block_comment:
            end = comment_style.block_comment_end
            if end and line[i:i + len(end)] == end:
                state.in_block_comment = False
                i += len(end)
            else:
                i += 1
            continue

        # --- Inside triple-quoted string (Python) ---
        if state.in_triple_quote:
            triple = state.string_char * 3
            if line[i:i + 3] == triple:
                state.in_triple_quote = False
                state.in_string = False
                state.string_char = None
                i += 3
            elif line[i] == '\\':
                i += 2  # skip escaped char
            else:
                i += 1
            continue

        # --- Inside regular string ---
        if state.in_string:
            if line[i] == '\\':
                i += 2  # skip escaped char
            elif line[i] == state.string_char:
                state.in_string = False
                state.string_char = None
                i += 1
            else:
                i += 1
            continue

        # --- Normal code ---
        char = line[i]

        # Check for line comment
        lc = comment_style.line_comment
        if lc and line[i:i + len(lc)] == lc:
            break  # rest of line is comment

        # Check for block comment start
        bc_start = comment_style.block_comment_start
        if bc_start and line[i:i + len(bc_start)] == bc_start:
            state.in_block_comment = True
            i += len(bc_start)
            continue

        # Check for triple-quote string (Python)
        if comment_style.triple_quote and char in comment_style.string_delimiters:
            triple = char * 3
            if line[i:i + 3] == triple:
                state.in_triple_quote = True
                state.in_string = True
                state.string_char = char
                i += 3
                continue

        # Check for string delimiter
        if char in comment_style.string_delimiters:
            state.in_string = True
            state.string_char = char
            i += 1
            continue

        # Real code character
        callback(char, i)
        i += 1

    return state


# =============================================================================
# Block Extraction Strategies
# =============================================================================

def extract_block_brace(
    lines: List[str],
    start_idx: int,
    comment_style: CommentStyle,
) -> int:
    """Find the end of a brace-delimited block.

    Scans from start_idx for the first '{', then counts nested braces
    until the matching '}' is found.

    Returns:
        Line index of the closing '}' (inclusive)

    Raises:
        ValueError: If no matching closing brace found
    """
    depth = 0
    found_opening = False
    state = ScanState()

    for line_idx in range(start_idx, len(lines)):
        def on_char(char, pos):
            nonlocal depth, found_opening
            if char == '{':
                depth += 1
                found_opening = True
            elif char == '}':
                depth -= 1

        scan_line(lines[line_idx], state, comment_style, on_char)

        if found_opening and depth == 0:
            return line_idx

    raise ValueError(f"No matching closing brace found from line {start_idx + 1}")


def extract_block_paren(
    lines: List[str],
    start_idx: int,
    comment_style: CommentStyle,
) -> int:
    """Find the end of a parenthesis-delimited block.

    Same logic as brace but counts '(' and ')'.

    Returns:
        Line index of the closing ')' (inclusive)

    Raises:
        ValueError: If no matching closing paren found
    """
    depth = 0
    found_opening = False
    state = ScanState()

    for line_idx in range(start_idx, len(lines)):
        def on_char(char, pos):
            nonlocal depth, found_opening
            if char == '(':
                depth += 1
                found_opening = True
            elif char == ')':
                depth -= 1

        scan_line(lines[line_idx], state, comment_style, on_char)

        if found_opening and depth == 0:
            return line_idx

    raise ValueError(f"No matching closing paren found from line {start_idx + 1}")


def extract_block_indent(
    lines: List[str],
    start_idx: int,
    comment_style: CommentStyle,
) -> int:
    """Find the end of an indentation-delimited block (Python).

    The block includes all subsequent lines with indentation strictly
    greater than the declaration line, plus intervening blank lines.
    Trailing blank lines are trimmed.

    Returns:
        Line index of the last line of the block (inclusive)
    """
    # Determine indentation of the declaration line
    decl_line = lines[start_idx]
    decl_indent = len(decl_line) - len(decl_line.lstrip())

    last_content_line = start_idx

    for line_idx in range(start_idx + 1, len(lines)):
        line = lines[line_idx]
        stripped = line.strip()

        # Blank lines are part of the block (don't break)
        if not stripped:
            continue

        # Non-blank line: check indent
        line_indent = len(line) - len(line.lstrip())
        if line_indent <= decl_indent:
            break

        last_content_line = line_idx

    return last_content_line


def extract_block_keyword(
    lines: List[str],
    start_idx: int,
    comment_style: CommentStyle,
    keyword_end: str = r'\bEND\b(?!\s+(?:IF|LOOP|WHILE|FOR|CASE)\b)',
) -> int:
    """Find the end of a keyword-delimited block (e.g., BEGIN/END).

    Handles nested BEGIN/END pairs. The END line (and optional trailing
    semicolon) is included. Compound terminators like END IF, END LOOP
    are ignored by default (they close control flow, not BEGIN blocks).

    Returns:
        Line index of the closing keyword (inclusive)

    Raises:
        ValueError: If no matching closing keyword found
    """
    begin_pattern = re.compile(r'\bBEGIN\b', re.IGNORECASE)
    end_pattern = re.compile(keyword_end, re.IGNORECASE)
    depth = 0
    found_begin = False
    state = ScanState()

    for line_idx in range(start_idx, len(lines)):
        # Collect real code characters (non-string, non-comment)
        real_chars = []

        def on_char(char, pos):
            real_chars.append((char, pos))

        scan_line(lines[line_idx], state, comment_style, on_char)

        # Reconstruct the "real code" portion for regex matching
        real_text = lines[line_idx]  # Use full line but only match if not in string
        # Simple approach: check for BEGIN/END in the raw line
        # The state machine ensures we skip lines that are entirely in comments/strings

        if not state.in_block_comment and not state.in_string:
            if begin_pattern.search(lines[line_idx]):
                depth += 1
                found_begin = True
            if end_pattern.search(lines[line_idx]):
                depth -= 1

            if found_begin and depth == 0:
                return line_idx

    raise ValueError(f"No matching closing keyword found from line {start_idx + 1}")


# =============================================================================
# Block Strategy Dispatch
# =============================================================================

BLOCK_STRATEGIES = {
    'brace': extract_block_brace,
    'paren': extract_block_paren,
    'indent': extract_block_indent,
}


def _extract_block(
    lines: List[str],
    start_idx: int,
    comment_style: CommentStyle,
    block_style: str,
    keyword_end: Optional[str] = None,
) -> int:
    """Dispatch to the appropriate block extraction strategy.

    Returns:
        End line index (inclusive)
    """
    if block_style == 'keyword':
        return extract_block_keyword(lines, start_idx, comment_style, keyword_end or r'\bEND\b(?!\s+(?:IF|LOOP|WHILE|FOR|CASE)\b)')
    strategy = BLOCK_STRATEGIES.get(block_style)
    if not strategy:
        raise ValueError(f"Unknown block style: {block_style}")
    return strategy(lines, start_idx, comment_style)


# =============================================================================
# Language Configurations
# =============================================================================

PYTHON_CONFIG = LanguageConfig(
    name="Python",
    extensions=["py"],
    comment_style=CommentStyle(
        line_comment="#",
        string_delimiters=['"', "'"],
        triple_quote=True,
    ),
    patterns=[
        SymbolPattern(
            kind="class",
            regex_template=r'^\s*class\s+{name}\s*[\(:]',
            block_style="indent",
            nestable=True,
        ),
        SymbolPattern(
            kind="function",
            regex_template=r'^\s*(?:async\s+)?def\s+{name}\s*\(',
            block_style="indent",
            nestable=True,
        ),
    ],
)

JS_TS_CONFIG = LanguageConfig(
    name="JavaScript/TypeScript",
    extensions=["js", "ts", "jsx", "tsx"],
    comment_style=CommentStyle(
        line_comment="//",
        block_comment_start="/*",
        block_comment_end="*/",
        string_delimiters=['"', "'", '`'],
    ),
    patterns=[
        SymbolPattern(
            kind="class",
            regex_template=r'^\s*(?:export\s+)?(?:default\s+)?class\s+{name}\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="function",
            regex_template=r'^\s*(?:export\s+)?(?:async\s+)?function\s+{name}\s*[\(<]',
            block_style="brace",
        ),
        SymbolPattern(
            kind="const/let/var",
            regex_template=r'^\s*(?:export\s+)?(?:const|let|var)\s+{name}\s*=',
            block_style="brace",
        ),
    ],
)

C_CPP_CONFIG = LanguageConfig(
    name="C/C++",
    extensions=["c", "cpp", "h", "hpp", "cc", "cxx"],
    comment_style=CommentStyle(
        line_comment="//",
        block_comment_start="/*",
        block_comment_end="*/",
    ),
    patterns=[
        SymbolPattern(
            kind="class",
            regex_template=r'^\s*class\s+{name}\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="struct",
            regex_template=r'^\s*(?:typedef\s+)?struct\s+{name}\b',
            block_style="brace",
        ),
        SymbolPattern(
            kind="function",
            regex_template=r'^\s*\S+[\s\*]+(?:\w+::)*{name}\s*\(',
            block_style="brace",
        ),
    ],
)

JAVA_CONFIG = LanguageConfig(
    name="Java",
    extensions=["java"],
    comment_style=CommentStyle(
        line_comment="//",
        block_comment_start="/*",
        block_comment_end="*/",
    ),
    patterns=[
        SymbolPattern(
            kind="class",
            regex_template=r'^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:abstract\s+)?class\s+{name}\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="interface",
            regex_template=r'^\s*(?:public\s+|private\s+|protected\s+)?interface\s+{name}\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="method",
            regex_template=r'^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:abstract\s+)?\S+\s+{name}\s*\(',
            block_style="brace",
        ),
    ],
)

CSHARP_CONFIG = LanguageConfig(
    name="C#",
    extensions=["cs"],
    comment_style=CommentStyle(
        line_comment="//",
        block_comment_start="/*",
        block_comment_end="*/",
    ),
    patterns=[
        SymbolPattern(
            kind="class",
            regex_template=r'^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+)?(?:abstract\s+)?(?:partial\s+)?class\s+{name}\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="interface",
            regex_template=r'^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?interface\s+{name}\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="method",
            regex_template=r'^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+)?(?:abstract\s+)?(?:virtual\s+)?(?:override\s+)?(?:async\s+)?\S+\s+{name}\s*[\(<]',
            block_style="brace",
        ),
    ],
)

SQL_CONFIG = LanguageConfig(
    name="SQL",
    extensions=["sql"],
    comment_style=CommentStyle(
        line_comment="--",
        block_comment_start="/*",
        block_comment_end="*/",
        string_delimiters=["'"],
    ),
    patterns=[
        SymbolPattern(
            kind="cte",
            regex_template=r'(?:^|,)\s*(?:WITH\s+)?{name}\s+AS\s*\(',
            block_style="paren",
            nestable=False,
        ),
        SymbolPattern(
            kind="procedure",
            regex_template=r'^\s*CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+{name}\b',
            block_style="keyword",
            keyword_end=r'\bEND\b(?!\s+(?:IF|LOOP|WHILE|FOR|CASE)\b)',
        ),
        SymbolPattern(
            kind="function",
            regex_template=r'^\s*CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+{name}\b',
            block_style="keyword",
            keyword_end=r'\bEND\b(?!\s+(?:IF|LOOP|WHILE|FOR|CASE)\b)',
        ),
    ],
)

# Build extension -> config lookup
ALL_CONFIGS = [PYTHON_CONFIG, JS_TS_CONFIG, C_CPP_CONFIG, JAVA_CONFIG, CSHARP_CONFIG, SQL_CONFIG]

_EXTENSION_MAP: Optional[Dict[str, LanguageConfig]] = None


def _get_extension_map() -> Dict[str, LanguageConfig]:
    """Build and cache extension -> LanguageConfig lookup."""
    global _EXTENSION_MAP
    if _EXTENSION_MAP is None:
        _EXTENSION_MAP = {}
        for config in ALL_CONFIGS:
            for ext in config.extensions:
                _EXTENSION_MAP[ext] = config
    return _EXTENSION_MAP


# =============================================================================
# Decorator Detection (Python)
# =============================================================================

def _include_decorators(lines: List[str], start_idx: int) -> int:
    """Scan backward from start_idx to include Python decorators.

    Returns the adjusted start index (may be earlier than start_idx).
    """
    idx = start_idx - 1
    while idx >= 0:
        stripped = lines[idx].strip()
        if stripped.startswith('@'):
            idx -= 1
        else:
            break
    return idx + 1


# =============================================================================
# Symbol Finding
# =============================================================================

def _find_symbol_in_range(
    lines: List[str],
    symbol_name: str,
    config: LanguageConfig,
    range_start: int,
    range_end: int,
) -> Optional[Tuple[int, int]]:
    """Find a symbol within a specific line range.

    Args:
        lines: All file lines
        symbol_name: Name to search for (single part, no dots)
        config: Language configuration
        range_start: Start line index (inclusive)
        range_end: End line index (inclusive)

    Returns:
        (start_idx, end_idx) tuple or None
    """
    escaped_name = re.escape(symbol_name)

    for pattern in config.patterns:
        regex_str = pattern.regex_template.replace('{name}', escaped_name)
        regex = re.compile(regex_str, re.IGNORECASE if config.name == "SQL" else 0)

        for line_idx in range(range_start, range_end + 1):
            if regex.search(lines[line_idx]):
                # Found the symbol declaration
                try:
                    end_idx = _extract_block(
                        lines, line_idx, config.comment_style,
                        pattern.block_style, pattern.keyword_end
                    )
                except ValueError:
                    continue

                # Include decorators for indent-based languages
                actual_start = line_idx
                if pattern.block_style == 'indent':
                    actual_start = _include_decorators(lines, line_idx)

                return (actual_start, end_idx)

    return None


# =============================================================================
# Public API
# =============================================================================

def get_language_config(file_path: str) -> Optional[LanguageConfig]:
    """Get language config for a file path.

    Args:
        file_path: Path to source file

    Returns:
        LanguageConfig or None if extension not recognized
    """
    ext = os.path.splitext(file_path)[1].lstrip('.')
    return _get_extension_map().get(ext)


def extract_symbol(
    content: str,
    symbol_name: str,
    file_path: str,
) -> Optional[Dict]:
    """Extract a code symbol from source content.

    Args:
        content: Full file content as string
        symbol_name: Name of symbol to extract. Supports dot notation
                     for nested symbols (e.g., 'MyClass.my_method').
        file_path: Path to source file (for language detection)

    Returns:
        {'lines': list[str], 'startLine': int} or None
    """
    config = get_language_config(file_path)
    if config is None:
        return None

    lines = content.replace('\r\n', '\n').split('\n')
    parts = symbol_name.split('.')

    # Resolve each part, narrowing the search range
    range_start = 0
    range_end = len(lines) - 1

    for i, part in enumerate(parts):
        result = _find_symbol_in_range(lines, part, config, range_start, range_end)
        if result is None:
            return None

        start_idx, end_idx = result

        if i < len(parts) - 1:
            # Not the last part - narrow range for next search
            # Search within the block body (skip the declaration line)
            range_start = start_idx + 1
            range_end = end_idx
        else:
            # Last part - this is what we return
            return {
                'lines': lines[start_idx:end_idx + 1],
                'startLine': start_idx + 1,
            }

    return None
