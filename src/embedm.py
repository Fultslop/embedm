import sys
import os
import re
from typing import Optional, Set, List, Dict

def parse_embed_options(embed_block_content: str) -> Dict:
    """
    Parses options from an embed block
    Extracts key:value pairs like "title: My Title" or "line_numbers: html"
    """
    options = {
        'title': None,
        'line_numbers': False  # False | 'text' | 'html'
    }
    
    lines = embed_block_content.split('\n')
    
    for line in lines:
        trimmed = line.strip()
        
        # Match "title: value" (capture everything after colon)
        title_match = re.match(r'^title:\s*(.+)$', trimmed, re.IGNORECASE)
        if title_match:
            options['title'] = title_match.group(1).strip()
            continue
        
        # Match "line_numbers: text/html/true/false"
        line_num_match = re.match(r'^line_numbers:\s*(.+)$', trimmed, re.IGNORECASE)
        if line_num_match:
            val = line_num_match.group(1).lower().strip()
            if val == 'text':
                options['line_numbers'] = 'text'
            elif val == 'html':
                options['line_numbers'] = 'html'
            elif val in ('true', 'yes', '1'):
                options['line_numbers'] = 'html'  # Default to html for backwards compatibility
            else:
                options['line_numbers'] = False
            continue
    
    return options


def extract_region(content: str, tag_name: str) -> Optional[Dict]:
    """
    Extracts a specific region marked by md.start:tagName and md.end:tagName
    Returns {'lines': list[str], 'startLine': int} or None
    """
    lines = content.replace('\r\n', '\n').split('\n')
    start_marker = f"md.start:{tag_name.strip()}"
    end_marker = f"md.end:{tag_name.strip()}"
    
    def normalize_marker(s):
        return re.sub(r'\s', '', s)
    
    start_index = -1
    end_index = -1
    
    for i, line in enumerate(lines):
        clean_line = normalize_marker(line)
        if normalize_marker(start_marker) in clean_line:
            start_index = i + 1
        elif normalize_marker(end_marker) in clean_line:
            end_index = i
            break
    
    if start_index == -1 or end_index == -1:
        return None
    
    return {
        'lines': lines[start_index:end_index],
        'startLine': start_index + 1
    }


def extract_lines(content: str, range_str: str) -> Optional[Dict]:
    """
    Extracts a range of lines based on L<start>-<end> syntax
    Returns {'lines': list[str], 'startLine': int} or None
    """
    lines = content.replace('\r\n', '\n').split('\n')
    
    # Handles L10, L10-20, L10-, and L10-L20
    match = re.match(r'^L(\d+)(?:-L?(\d+)?)?$', range_str, re.IGNORECASE)
    
    if not match:
        return None
    
    start_line = int(match.group(1))
    has_dash = '-' in range_str
    # If there's a dash but no second number (L10-), go to the end
    end_line_param = int(match.group(2)) if match.group(2) else (len(lines) if has_dash else start_line)
    
    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line_param)
    
    return {
        'lines': lines[start_idx:end_idx],
        'startLine': start_line
    }


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


def csv_to_markdown_table(csv_content: str) -> str:
    """
    Converts CSV content to a Markdown table
    """
    lines = csv_content.strip().split('\n')
    if not lines or not csv_content.strip():  # Handle empty input
        return ''
    
    # Parse CSV (simple parser - handles basic cases)
    def parse_csv_line(line):
        cells = []
        current = ''
        in_quotes = False
        i = 0
        
        while i < len(line):
            char = line[i]
            next_char = line[i + 1] if i + 1 < len(line) else None
            
            if char == '"':
                if in_quotes and next_char == '"':
                    # Escaped quote
                    current += '"'
                    i += 1  # Skip next quote
                else:
                    # Toggle quote mode
                    in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                # End of cell
                cells.append(current.strip())
                current = ''
            else:
                current += char
            
            i += 1
        
        # Push last cell
        cells.append(current.strip())
        return cells
    
    rows = [parse_csv_line(line) for line in lines]
    if not rows:
        return ''
    
    # Build markdown table
    max_cols = max(len(r) for r in rows)
    header = rows[0]
    data_rows = rows[1:]
    
    # Header row
    table = '| ' + ' | '.join(cell if cell else ' ' for cell in header) + ' |\n'
    
    # Separator row
    table += '| ' + ' | '.join('---' for _ in header) + ' |\n'
    
    # Data rows
    for row in data_rows:
        # Pad row if it has fewer columns than header
        while len(row) < max_cols:
            row.append('')
        table += '| ' + ' | '.join(cell if cell else ' ' for cell in row) + ' |\n'
    
    return table.rstrip()


def slugify(text: str) -> str:
    """
    Generates a GitHub-style anchor slug from a heading
    """
    result = text.lower().strip()
    result = re.sub(r'[^\w\s-]', '', result)  # Remove special chars
    result = re.sub(r'[\s_]+', '-', result)   # Replace spaces with hyphens
    result = re.sub(r'^-+|-+$', '', result)   # Remove leading/trailing hyphens
    return result


def generate_table_of_contents(content: str) -> str:
    """
    Generates a table of contents from markdown headings
    """
    # Normalize line endings first
    lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    toc_lines = []
    heading_counts = {}  # Track duplicate headings for unique anchors
    
    for line in lines:
        # Match markdown headings (# through ######)
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if not match:
            continue
        
        level = len(match.group(1))
        text = match.group(2).strip()
        
        # Generate slug (GitHub style)
        slug = slugify(text)
        
        # Handle duplicate headings by appending -1, -2, etc.
        if slug in heading_counts:
            heading_counts[slug] += 1
            slug = f"{slug}-{heading_counts[slug]}"
        else:
            heading_counts[slug] = 0
        
        # Create indentation (2 spaces per level beyond h1)
        indent = '  ' * (level - 1)
        
        # Add to TOC
        toc_lines.append(f"{indent}- [{text}](#{slug})")
    
    return '\n'.join(toc_lines) if toc_lines else '> [!NOTE]\n> No headings found in document.'


def resolve_content(absolute_file_path: str, processing_stack: Optional[Set[str]] = None) -> str:
    """
    Recursive Resolver with Path Scoping
    """
    if processing_stack is None:
        processing_stack = set()
    
    if absolute_file_path in processing_stack:
        return f"> [!CAUTION]\n> **MdEmbed Error:** Infinite loop detected! `{os.path.basename(absolute_file_path)}` is trying to embed a parent."
    
    if not os.path.exists(absolute_file_path) or os.path.isdir(absolute_file_path):
        return f"> [!CAUTION]\n> **MdEmbed Error:** File not found: `{absolute_file_path}`"
    
    processing_stack.add(absolute_file_path)
    
    with open(absolute_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_file_dir = os.path.dirname(absolute_file_path)
    
    # Regex to find ```embed file:path.ext#fragment ... ```
    embed_regex = re.compile(r'^```embed\s+([\s\S]*?)```', re.MULTILINE)
    
    def replace_embed(match):
        embed_content = match.group(1)
        lines = embed_content.strip().split('\n')
        first_line = lines[0].strip()
        
        # Parse the file reference from first line
        file_match = re.match(r'^file:\s*([^\s]+)', first_line)
        if not file_match:
            # Not a file embed (might be table_of_contents)
            return match.group(0)
        
        file_reference = file_match.group(1)
        options = parse_embed_options(embed_content)
        
        clean_ref = file_reference.strip()
        parts = clean_ref.split('#', 1)
        rel_path = parts[0]
        fragment = parts[1] if len(parts) > 1 else None
        
        target_path = os.path.abspath(os.path.join(current_file_dir, rel_path))
        is_markdown = target_path.endswith('.md')
        
        if not os.path.exists(target_path):
            return f"> [!CAUTION]\n> File not found: `{rel_path}` relative to `{current_file_dir}`"
        
        with open(target_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # Case A: Embedding specific part (Fragment) or non-Markdown file
        if fragment or not is_markdown:
            result_data = None
            ext = os.path.splitext(target_path)[1][1:] or 'text'
            
            if fragment:
                # Try L10-20 format first
                result_data = extract_lines(raw_content, fragment)
                # If not L-format, try named region tags
                if not result_data:
                    result_data = extract_region(raw_content, fragment)
                
                if not result_data:
                    return f"> [!CAUTION]\n> Fragment `{fragment}` not found in `{rel_path}`"
                
                # Apply line numbers if requested
                if options['line_numbers'] == 'html':
                    raw_content = format_with_line_numbers(result_data['lines'], result_data['startLine'], ext)
                elif options['line_numbers'] == 'text':
                    raw_content = format_with_line_numbers_text(result_data['lines'], result_data['startLine'])
                else:
                    # Just dedent the lines without numbers
                    raw_content = dedent_lines(result_data['lines'])
            
            # Special handling for CSV files - convert to markdown table
            if ext == 'csv' and not fragment:
                table = csv_to_markdown_table(raw_content)
                # Wrap in optional title
                if options['title']:
                    return f"**{options['title']}**\n\n{table}"
                return table
            
            # Build result with optional title
            result = ''
            if options['title']:
                result += f"**{options['title']}**\n\n"
            
            # If we formatted with HTML line numbers, return as-is (no code block wrapper)
            if options['line_numbers'] == 'html' and fragment:
                result += raw_content
            else:
                # Standard markdown code block (for text line numbers or no line numbers)
                result += f"```{ext}\n{raw_content.rstrip()}\n```"
            
            return result
        
        # Case B: Embedding another Markdown file recursively
        embedded_md = resolve_content(target_path, set(processing_stack))
        
        # Add title if specified
        if options['title']:
            return f"**{options['title']}**\n\n{embedded_md}"
        
        return embedded_md
    
    resolved = embed_regex.sub(replace_embed, content)
    return resolved


def resolve_table_of_contents(content: str) -> str:
    """
    Post-process to resolve table_of_contents embeds
    """
    # Match ```embed\ntable_of_contents\n``` or ```embed table_of_contents```
    # Use [\s\S] to match any character including newlines
    toc_regex = re.compile(r'```embed[\s]+table_of_contents[\s]*```', re.MULTILINE)
    
    # First, remove all table_of_contents embeds temporarily to get the "final" content
    content_without_toc_embeds = toc_regex.sub('', content)
    
    # Generate TOC from the content without the embed markers
    toc = generate_table_of_contents(content_without_toc_embeds)
    
    # Now replace all table_of_contents embeds with the generated TOC
    return toc_regex.sub(lambda m: toc, content)

# --- Entry Point ---
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:\n  Single file: python mdembed.py <file.md>\n  Directory:   python mdembed.py <source_dir> <output_dir>")
        sys.exit(1)
    
    source_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        absolute_source = os.path.abspath(source_path)
        
        if os.path.isfile(absolute_source):
            # First pass: resolve file embeds
            final_content = resolve_content(absolute_source)
            
            # Second pass: resolve table of contents (after all embeds are done)
            final_content = resolve_table_of_contents(final_content)
            
            target = os.path.abspath(output_path) if output_path else absolute_source.replace('.md', '.compiled.md')
            
            with open(target, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            print(f"✅ Compiled: {target}")
            
        elif os.path.isdir(absolute_source):
            if not output_path:
                raise Exception("Output directory required for directory mode.")
            
            absolute_output = os.path.abspath(output_path)
            os.makedirs(absolute_output, exist_ok=True)
            
            for filename in os.listdir(absolute_source):
                if filename.endswith('.md'):
                    # First pass: resolve file embeds
                    final_content = resolve_content(os.path.join(absolute_source, filename))
                    
                    # Second pass: resolve table of contents
                    final_content = resolve_table_of_contents(final_content)
                    
                    with open(os.path.join(absolute_output, filename), 'w', encoding='utf-8') as f:
                        f.write(final_content)
                    
                    print(f"✅ {filename} -> {absolute_output}")
        
    except Exception as err:
        print(f"❌ Critical Error: {err}")
        sys.exit(1)