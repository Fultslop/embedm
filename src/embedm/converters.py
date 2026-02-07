"""File format converters and table of contents generation."""

import re


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
