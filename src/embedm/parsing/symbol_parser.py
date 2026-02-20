"""Language-aware code symbol extraction.

Extracts named symbols (class, method, function, etc.) from source files using
regex-based declaration matching and brace-depth block extraction.

Architecture (bottom to top):
1. String/comment state machine  — skips literals when counting braces
2. Block extraction              — brace and rest-of-file strategies
3. Declarative language configs  — per-language symbol patterns
4. Public API                    — get_language_config, extract_symbol
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class CommentStyle:
    """Defines how a language handles comments and string literals."""

    line_comment: str | None = None
    block_comment_start: str | None = None
    block_comment_end: str | None = None
    string_delimiters: list[str] = field(default_factory=lambda: ['"', "'"])


@dataclass
class SymbolPattern:
    """A regex pattern for matching one symbol kind within a language.

    Attributes:
        kind: Human-readable label (e.g. 'class', 'method').
        regex_template: Regex with {name} placeholder for the symbol name.
        block_style: One of 'brace' or 'rest_of_file'.
        nestable: Whether the symbol can contain other nestable symbols (for dot-notation scoping).
    """

    kind: str
    regex_template: str
    block_style: str
    nestable: bool = True


@dataclass
class LanguageConfig:
    """Complete language definition for symbol extraction.

    Attributes:
        name: Language name (for error messages).
        extensions: File extensions handled by this config (without leading dot).
        comment_style: Comment and string literal rules.
        patterns: Ordered list of SymbolPatterns to try during search.
    """

    name: str
    extensions: list[str]
    comment_style: CommentStyle
    patterns: list[SymbolPattern]


@dataclass
class _ScanState:
    """Tracks comment/string state across lines during brace scanning."""

    in_block_comment: bool = False
    in_string: bool = False
    string_char: str | None = None


@dataclass
class _SymbolSpec:
    """Parsed symbol specification from user input.

    Attributes:
        parts: Dot-separated name components (e.g. ['MyNs', 'MyClass', 'MyMethod']).
        signature: Parameter type string if present (e.g. 'string, int'), or None.
        has_parens: Whether parentheses were explicitly given (disambiguates overloads).
    """

    parts: list[str]
    signature: str | None = None
    has_parens: bool = False


# ---------------------------------------------------------------------------
# String / comment state machine
# ---------------------------------------------------------------------------

_PARAM_MODIFIERS = ("ref ", "out ", "in ", "params ", "this ", "final ")


def _step_block_comment(line: str, i: int, state: _ScanState, style: CommentStyle) -> int:
    end = style.block_comment_end
    if end and line[i : i + len(end)] == end:
        state.in_block_comment = False
        i += len(end)
    else:
        i += 1
    return i


def _step_string(line: str, i: int, state: _ScanState) -> int:
    if line[i] == "\\":
        i += 2
    else:
        if line[i] == state.string_char:
            state.in_string = False
            state.string_char = None
        i += 1
    return i


def _scan_line(line: str, state: _ScanState, style: CommentStyle) -> tuple[str, _ScanState]:
    """Return the 'real code' portion of a line (non-string, non-comment characters).

    Mutates state in place to track block comments and strings across lines.
    """
    real: list[str] = []
    i = 0
    length = len(line)

    while i < length:
        if state.in_block_comment:
            i = _step_block_comment(line, i, state, style)
            continue

        if state.in_string:
            i = _step_string(line, i, state)
            continue

        char = line[i]

        lc = style.line_comment
        if lc and line[i : i + len(lc)] == lc:
            break

        bc_start = style.block_comment_start
        if bc_start and line[i : i + len(bc_start)] == bc_start:
            state.in_block_comment = True
            i += len(bc_start)
            continue

        if char in style.string_delimiters:
            state.in_string = True
            state.string_char = char
            i += 1
            continue

        real.append(char)
        i += 1

    return "".join(real), state


# ---------------------------------------------------------------------------
# Block extraction
# ---------------------------------------------------------------------------


def _extract_block_brace(lines: list[str], start_idx: int, style: CommentStyle) -> int:
    """Find the closing brace of a brace-delimited block.

    Scans from start_idx for the first '{', then tracks nesting depth until
    the matching '}' is found, skipping braces inside strings and comments.

    Returns the line index of the closing '}' (inclusive).
    Raises ValueError if no matching closing brace is found.
    """
    depth = 0
    found_opening = False
    state = _ScanState()

    for line_idx in range(start_idx, len(lines)):
        real, state = _scan_line(lines[line_idx], state, style)
        for char in real:
            if char == "{":
                depth += 1
                found_opening = True
            elif char == "}":
                depth -= 1
        if found_opening and depth == 0:
            return line_idx

    raise ValueError(f"no matching closing brace from line {start_idx + 1}")


def _extract_block_rest_of_file(lines: list[str], _start_idx: int, _style: CommentStyle) -> int:
    """Block extends to the end of the file (e.g. C# file-scoped namespace)."""
    return len(lines) - 1


def _find_block_start(lines: list[str], start_idx: int, style: CommentStyle) -> int:
    """Return the line index of the opening '{' of a block, scanning from start_idx."""
    state = _ScanState()
    for line_idx in range(start_idx, len(lines)):
        real, state = _scan_line(lines[line_idx], state, style)
        if "{" in real:
            return line_idx
    raise ValueError(f"no opening brace from line {start_idx + 1}")


_BLOCK_STRATEGIES = {
    "brace": _extract_block_brace,
    "rest_of_file": _extract_block_rest_of_file,
}


def _extract_block(lines: list[str], start_idx: int, style: CommentStyle, block_style: str) -> int:
    """Dispatch to the appropriate block extraction strategy.

    Returns the end line index (inclusive).
    Raises ValueError for an unknown block style.
    """
    strategy = _BLOCK_STRATEGIES.get(block_style)
    if strategy is None:
        raise ValueError(f"unknown block style: '{block_style}'")
    return strategy(lines, start_idx, style)


# ---------------------------------------------------------------------------
# Language configurations
# ---------------------------------------------------------------------------

_C_COMMENT = CommentStyle(
    line_comment="//",
    block_comment_start="/*",
    block_comment_end="*/",
)

C_CPP_CONFIG = LanguageConfig(
    name="C/C++",
    extensions=["c", "cpp", "h", "hpp", "cc", "cxx"],
    comment_style=_C_COMMENT,
    patterns=[
        SymbolPattern(
            kind="namespace",
            regex_template=r"^\s*namespace\s+{name}\b",
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="class",
            regex_template=r"^\s*class\s+{name}\b",
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="struct",
            regex_template=r"^\s*(?:typedef\s+)?struct\s+{name}\b",
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="enum",
            regex_template=r"^\s*(?:typedef\s+)?enum\s+(?:class\s+)?{name}\b",
            block_style="brace",
            nestable=False,
        ),
        SymbolPattern(
            kind="function",
            regex_template=r"^\s*\S+[\s\*]+(?:\w+::)*{name}\s*\(",
            block_style="brace",
            nestable=False,
        ),
    ],
)

CSHARP_CONFIG = LanguageConfig(
    name="C#",
    extensions=["cs"],
    comment_style=_C_COMMENT,
    patterns=[
        SymbolPattern(
            kind="namespace_file_scoped",
            regex_template=r"^\s*namespace\s+{name}\s*;",
            block_style="rest_of_file",
            nestable=True,
        ),
        SymbolPattern(
            kind="namespace",
            regex_template=r"^\s*namespace\s+{name}\b",
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="class",
            regex_template=(
                r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?"
                r"(?:static\s+)?(?:abstract\s+)?(?:partial\s+)?class\s+{name}\b"
            ),
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="struct",
            regex_template=(r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:readonly\s+)?struct\s+{name}\b"),
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="interface",
            regex_template=r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?interface\s+{name}\b",
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="enum",
            regex_template=r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?enum\s+{name}\b",
            block_style="brace",
            nestable=False,
        ),
        SymbolPattern(
            kind="method",
            regex_template=(
                r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?"
                r"(?:static\s+)?(?:abstract\s+)?(?:virtual\s+)?(?:override\s+)?(?:async\s+)?"
                r"\S+\s+{name}\s*[\(<]"
            ),
            block_style="brace",
            nestable=False,
        ),
    ],
)

JAVA_CONFIG = LanguageConfig(
    name="Java",
    extensions=["java"],
    comment_style=_C_COMMENT,
    patterns=[
        SymbolPattern(
            kind="class",
            regex_template=(
                r"^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:abstract\s+)?class\s+{name}\b"
            ),
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="interface",
            regex_template=r"^\s*(?:public\s+|private\s+|protected\s+)?interface\s+{name}\b",
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="enum",
            regex_template=r"^\s*(?:public\s+|private\s+|protected\s+)?enum\s+{name}\b",
            block_style="brace",
            nestable=False,
        ),
        SymbolPattern(
            kind="method",
            regex_template=(
                r"^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:abstract\s+)?\S+\s+{name}\s*\("
            ),
            block_style="brace",
            nestable=False,
        ),
    ],
)

_EXTENSION_MAP: dict[str, LanguageConfig] = {
    ext: config for config in [C_CPP_CONFIG, CSHARP_CONFIG, JAVA_CONFIG] for ext in config.extensions
}


# ---------------------------------------------------------------------------
# Signature matching (overload disambiguation)
# ---------------------------------------------------------------------------


def _split_params(param_string: str) -> list[str]:
    """Split a parameter string on commas, respecting angle-bracket nesting."""
    if not param_string.strip():
        return []

    params: list[str] = []
    current: list[str] = []
    depth = 0

    for char in param_string:
        if char == "<":
            depth += 1
            current.append(char)
        elif char == ">":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            params.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    last = "".join(current).strip()
    if last:
        params.append(last)
    return params


def _extract_type_name(param: str) -> str:
    """Extract the type from a single 'type name' or 'type' parameter string."""
    param = param.strip()
    angle_depth = 0
    last_space = -1

    for i, char in enumerate(param):
        if char == "<":
            angle_depth += 1
        elif char == ">":
            angle_depth -= 1
        elif char == " " and angle_depth == 0:
            last_space = i

    return param[:last_space] if last_space > 0 else param


def _finalize_params(collected: list[str]) -> list[str]:
    param_str = "".join(collected).strip()
    if not param_str:
        return []
    types: list[str] = []
    for p in _split_params(param_str):
        p = p.strip()
        if not p:
            continue
        eq = p.find("=")
        if eq != -1:
            p = p[:eq].strip()
        p_lower = p.lower()
        for mod in _PARAM_MODIFIERS:
            if p_lower.startswith(mod):
                p = p[len(mod) :].strip()
                break
        types.append(_extract_type_name(p))
    return types


def _extract_param_types(lines: list[str], decl_idx: int) -> list[str] | None:
    """Extract parameter types from a declaration starting at decl_idx.

    Scans forward up to 10 lines to collect the full parameter list.
    Returns a list of type strings, [] for no parameters, or None if unparseable.
    """
    collected: list[str] = []
    found_open = False
    depth = 0

    for idx in range(decl_idx, min(decl_idx + 10, len(lines))):
        for char in lines[idx]:
            if not found_open:
                if char == "(":
                    found_open = True
                    depth = 1
            else:
                if char == "(":
                    depth += 1
                    collected.append(char)
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        return _finalize_params(collected)
                    collected.append(char)
                else:
                    collected.append(char)

    return None


def _match_signature(requested: list[str], declared: list[str]) -> bool:
    """Return True if requested parameter types match declared parameter types.

    Comparison is case-insensitive. Supports suffix matching for namespaced types
    (e.g. 'String' matches 'System.String').
    """
    if len(requested) != len(declared):
        return False
    for req, decl in zip(requested, declared, strict=True):
        req_l = req.strip().lower()
        decl_l = decl.strip().lower()
        if req_l == decl_l or decl_l.endswith("." + req_l):
            continue
        return False
    return True


# ---------------------------------------------------------------------------
# Spec parsing
# ---------------------------------------------------------------------------


def _parse_symbol_spec(symbol_name: str) -> _SymbolSpec:
    """Parse a possibly dotted or overloaded symbol specification.

    Examples:
        'MyClass'                 -> parts=['MyClass'], no signature
        'MyClass.MyMethod'        -> parts=['MyClass', 'MyMethod'], no signature
        'MyMethod(string, int)'   -> parts=['MyMethod'], signature='string, int'
        'Ns.MyClass.MyMethod()'   -> parts=['Ns', 'MyClass', 'MyMethod'], signature=''
    """
    name = symbol_name.strip()

    if name.endswith(")"):
        depth = 0
        for i in range(len(name) - 1, -1, -1):
            if name[i] == ")":
                depth += 1
            elif name[i] == "(":
                depth -= 1
                if depth == 0 and i > 0:
                    sig = name[i + 1 : -1]
                    parts = name[:i].split(".")
                    return _SymbolSpec(parts=parts, signature=sig, has_parens=True)
                break

    return _SymbolSpec(parts=name.split("."), signature=None, has_parens=False)


# ---------------------------------------------------------------------------
# Symbol search
# ---------------------------------------------------------------------------


def _parse_requested_params(signature: str | None, has_parens: bool) -> list[str] | None:
    if has_parens and signature:
        return _split_params(signature)
    return [] if has_parens else None


def _count_braces(real: str) -> int:
    count = 0
    for char in real:
        if char == "{":
            count += 1
        elif char == "}":
            count -= 1
    return count


def _try_match_at_line(
    lines: list[str],
    line_idx: int,
    pattern: SymbolPattern,
    regex: re.Pattern[str],
    requested_params: list[str] | None,
    config: LanguageConfig,
) -> int | None:
    if not regex.search(lines[line_idx]):
        return None
    if requested_params is not None:
        declared = _extract_param_types(lines, line_idx)
        if declared is None or not _match_signature(requested_params, declared):
            return None
    try:
        return _extract_block(lines, line_idx, config.comment_style, pattern.block_style)
    except ValueError:
        return None


def _find_symbol_in_range(
    lines: list[str],
    name: str,
    config: LanguageConfig,
    range_start: int,
    range_end: int,
    signature: str | None,
    has_parens: bool,
    restrict_depth: bool = False,
) -> tuple[int, int, str] | None:
    """Search for a symbol declaration within a line range.

    When restrict_depth is True, only matches at brace depth 0 (direct members).
    Returns (start_idx, end_idx, block_style) or None if not found.
    """
    requested_params = _parse_requested_params(signature, has_parens)
    escaped = re.escape(name)

    for pattern in config.patterns:
        regex = re.compile(pattern.regex_template.replace("{name}", escaped))
        scan_state = _ScanState()
        depth = 0

        for line_idx in range(range_start, range_end + 1):
            if restrict_depth:
                real, scan_state = _scan_line(lines[line_idx], scan_state, config.comment_style)
                at_depth = depth == 0
            else:
                at_depth = True

            if at_depth:
                end_idx = _try_match_at_line(lines, line_idx, pattern, regex, requested_params, config)
                if end_idx is not None:
                    return (line_idx, end_idx, pattern.block_style)

            if restrict_depth:
                depth += _count_braces(real)

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _sig_and_parens(spec: _SymbolSpec, is_last: bool) -> tuple[str | None, bool]:
    return (spec.signature, spec.has_parens) if is_last else (None, False)


def _find_with_coalescing(
    lines: list[str],
    spec: _SymbolSpec,
    i: int,
    config: LanguageConfig,
    range_start: int,
    range_end: int,
) -> tuple[int, tuple[int, int, str]] | None:
    """Find the symbol at spec.parts[i] with greedy coalescing of subsequent parts.

    Returns (matched_part_index, (start_idx, end_idx, block_style)) or None.
    """
    part = spec.parts[i]
    restrict = i > 0
    sig, parens = _sig_and_parens(spec, i == len(spec.parts) - 1)
    result = _find_symbol_in_range(lines, part, config, range_start, range_end, sig, parens, restrict)
    if result is not None:
        return (i, result)

    for j in range(i + 1, len(spec.parts)):
        part = part + "." + spec.parts[j]
        sig, parens = _sig_and_parens(spec, j == len(spec.parts) - 1)
        result = _find_symbol_in_range(lines, part, config, range_start, range_end, sig, parens, restrict)
        if result is not None:
            return (j, result)

    return None


def get_language_config(file_path: str) -> LanguageConfig | None:
    """Return the LanguageConfig for the given file path, or None if unsupported."""
    ext = Path(file_path).suffix.lstrip(".")
    return _EXTENSION_MAP.get(ext)


def extract_symbol(content: str, symbol_name: str, config: LanguageConfig) -> list[str] | None:
    """Extract a named code symbol from source content.

    Supports dot notation for scoped lookup (e.g. 'MyClass.MyMethod') and
    optional parameter signature for overload disambiguation (e.g. 'MyMethod(string, int)').

    Returns the extracted lines, or None if the symbol is not found.
    """
    lines = content.replace("\r\n", "\n").split("\n")
    spec = _parse_symbol_spec(symbol_name)
    range_start = 0
    range_end = len(lines) - 1
    i = 0

    while i < len(spec.parts):
        found = _find_with_coalescing(lines, spec, i, config, range_start, range_end)
        if found is None:
            return None
        i, result = found
        start_idx, end_idx, block_style = result
        if i < len(spec.parts) - 1:
            if block_style == "brace":
                brace_line = _find_block_start(lines, start_idx, config.comment_style)
                range_start = brace_line + 1
            else:
                range_start = start_idx + 1
            range_end = end_idx
        else:
            return lines[start_idx : end_idx + 1]
        i += 1

    return None
