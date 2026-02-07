"""Code formatting utilities for line numbers and indentation."""

import re
from typing import List


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


def format_with_line_numbers(lines: List[str], start_line: int, language: str = 'text') -> str:
    """
    Formats code with HTML line numbers that are non-selectable
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

    # Return HTML with embedded CSS
    return f'''<div class="code-block-with-lines">
<style>
.code-block-with-lines {{
  background: #f6f8fa;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
}}
.code-block-with-lines pre {{
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.5;
}}
.code-block-with-lines .line {{
  display: block;
}}
.code-block-with-lines .line-number {{
  display: inline-block;
  width: {max_digits + 1}ch;
  margin-right: 16px;
  color: #57606a;
  text-align: right;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}}
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
