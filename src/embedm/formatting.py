"""Code formatting utilities for line numbers and indentation."""

import os
import re
from pathlib import Path
from typing import List


# Cache for loaded CSS styles
_css_cache = {}


def load_line_number_style(style_spec: str, current_file_dir: str = None) -> str:
    """
    Load CSS for line numbers.

    Args:
        style_spec: Theme name ('default', 'dark', 'minimal') or path to CSS file
        current_file_dir: Directory of the file containing the embed (for resolving relative paths)

    Returns:
        CSS content as string
    """
    # Check cache first
    cache_key = (style_spec, current_file_dir)
    if cache_key in _css_cache:
        return _css_cache[cache_key]

    css_content = None

    # Check if it's a file path (relative or absolute)
    if current_file_dir and style_spec not in ('default', 'dark', 'minimal'):
        # Try resolving as relative path first
        relative_path = os.path.join(current_file_dir, style_spec)
        if os.path.exists(relative_path):
            try:
                with open(relative_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
            except Exception:
                pass  # Fall through to other options

    # Check if it's an absolute path
    if css_content is None and os.path.isabs(style_spec) and os.path.exists(style_spec):
        try:
            with open(style_spec, 'r', encoding='utf-8') as f:
                css_content = f.read()
        except Exception:
            pass  # Fall through to built-in themes

    # Try as built-in theme name
    if css_content is None:
        styles_dir = Path(__file__).parent / 'styles'
        theme_file = styles_dir / f'{style_spec}.css'

        if theme_file.exists():
            css_content = theme_file.read_text(encoding='utf-8')
        else:
            # Fallback to default theme
            default_file = styles_dir / 'default.css'
            css_content = default_file.read_text(encoding='utf-8')

    # Cache the result
    _css_cache[cache_key] = css_content
    return css_content


def format_with_line_numbers_text(lines: List[str], start_line: int) -> str:
    """
    Formats code with text-based line numbers (original format)
    """
    if not lines:
        return ""

    # Remove common leading whitespace
    non_empty_lines = [line for line in lines if line.strip()]
    if non_empty_lines:
        min_indent = min(len(re.match(r'^(\s*)', line).group(0)) for line in non_empty_lines)
    else:
        min_indent = 0

    clean_lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]

    # Calculate padding based on the highest line number
    max_digits = len(str(start_line + len(clean_lines) - 1))

    result = []
    for index, line in enumerate(clean_lines):
        current_num = str(start_line + index).rjust(max_digits)
        result.append(f"{current_num} | {line}")

    return '\n'.join(result)


def format_with_line_numbers(lines: List[str], start_line: int, language: str = 'text',
                             style: str = 'default', current_file_dir: str = None) -> str:
    """
    Formats code with HTML line numbers that are non-selectable

    Args:
        lines: Code lines to format
        start_line: Starting line number
        language: Language for syntax highlighting hint
        style: CSS theme name ('default', 'dark', 'minimal') or path to CSS file
        current_file_dir: Directory of the file containing the embed (for resolving relative CSS paths)

    Returns:
        HTML string with line numbers and styling
    """
    if not lines:
        return ""

    # Remove common leading whitespace
    non_empty_lines = [line for line in lines if line.strip()]
    if non_empty_lines:
        min_indent = min(len(re.match(r'^(\s*)', line).group(0)) for line in non_empty_lines)
    else:
        min_indent = 0

    clean_lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]

    # Calculate padding based on the highest line number
    max_digits = len(str(start_line + len(clean_lines) - 1))

    # Escape HTML entities
    def escape_html(s):
        return (s.replace('&', '&amp;')
                 .replace('<', '&lt;')
                 .replace('>', '&gt;')
                 .replace('"', '&quot;')
                 .replace("'", '&#039;'))

    # Build HTML
    code_lines = []
    for index, line in enumerate(clean_lines):
        current_num = str(start_line + index).rjust(max_digits)
        escaped_line = escape_html(line)
        code_lines.append(f'<span class="line"><span class="line-number">{current_num}</span>{escaped_line}\n</span>')

    code_lines_str = ''.join(code_lines)

    # Load CSS and replace placeholder
    css_content = load_line_number_style(style, current_file_dir)
    css_content = css_content.replace('{{max_digits}}', str(max_digits + 1))

    # Determine theme name for class
    # Extract basename without extension for custom CSS files, otherwise use style name
    if style in ('default', 'dark', 'minimal'):
        theme_name = style
    else:
        # For custom CSS paths, extract the filename without extension
        theme_name = Path(style).stem if '.' in style else style

    # Return HTML with embedded CSS
    return f'''<div class="code-block-{theme_name}">
<style>
{css_content}
</style>
<pre><code class="language-{language}">{code_lines_str}</code></pre>
</div>'''


def dedent_lines(lines: List[str]) -> str:
    """
    Removes common leading whitespace from lines and returns as string
    """
    if not lines:
        return ""

    non_empty_lines = [line for line in lines if line.strip()]
    if non_empty_lines:
        min_indent = min(len(re.match(r'^(\s*)', line).group(0)) for line in non_empty_lines)
    else:
        min_indent = 0

    return '\n'.join(line[min_indent:] if len(line) >= min_indent else line for line in lines)
