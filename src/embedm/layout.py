"""Layout processing for multi-column/row embeds."""

import re
from typing import Dict, Set, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .resolver import ProcessingContext


def parse_size(size_str: str) -> tuple[str, str]:
    """
    Parse size specification into value and unit.

    Args:
        size_str: Size like "30%", "300px", or "auto"

    Returns:
        Tuple of (value, unit) like ("30", "%") or ("300", "px") or ("auto", "")
    """
    if not size_str or size_str.lower() == 'auto':
        return ('auto', '')

    # Match number followed by optional unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*(%|px)?$', str(size_str).strip())
    if match:
        value = match.group(1)
        unit = match.group(2) or 'px'  # default to px if no unit
        return (value, unit)

    return ('auto', '')


def size_to_flex(size_str: str) -> str:
    """
    Convert size specification to CSS flex property.

    Args:
        size_str: Size like "30%", "300px", or "auto"

    Returns:
        CSS flex value like "0 0 30%" or "0 0 300px" or "1 1 auto"
    """
    value, unit = parse_size(size_str)

    if value == 'auto':
        return "1 1 auto"

    return f"0 0 {value}{unit}"


def parse_border(border_str: str) -> str:
    """
    Parse border specification into CSS border property.

    Args:
        border_str: Border like "1px solid #ccc" or "2px #000" or "true"

    Returns:
        CSS border value
    """
    if not border_str:
        return ''

    border_str = str(border_str).strip()

    if border_str.lower() in ('true', 'yes', '1'):
        return '1px solid #ccc'

    if border_str.lower() in ('false', 'no', '0'):
        return ''

    # If it's just "1px #color", add "solid"
    parts = border_str.split()
    if len(parts) == 2 and parts[0].endswith('px'):
        return f"{parts[0]} solid {parts[1]}"

    # Already looks like CSS border, return as-is
    return border_str


def process_layout_embed(properties: Dict, current_file_dir: str, processing_stack: Set[str], context: Optional['ProcessingContext'] = None) -> str:
    """
    Process a layout embed directive.

    Args:
        properties: Layout properties from YAML
        current_file_dir: Directory of the file containing the embed
        processing_stack: Set of files being processed
        context: Processing context with limits

    Returns:
        HTML string with flexbox layout
    """
    # Import here to avoid circular dependency
    from .processors import process_file_embed
    from .converters import generate_table_of_contents
    from .parsing import parse_yaml_embed_block

    # Extract properties
    orientation = properties.get('orientation', 'row')
    if orientation not in ('row', 'column'):
        return f"> [!CAUTION]\n> **Layout Error:** orientation must be 'row' or 'column', got '{orientation}'"

    gap = properties.get('gap', '0')
    border = properties.get('border')
    padding = properties.get('padding')
    background = properties.get('background')
    overflow = properties.get('overflow')
    overflow_x = properties.get('overflow-x')
    overflow_y = properties.get('overflow-y')
    max_height = properties.get('max-height')
    max_width = properties.get('max-width')
    min_height = properties.get('min-height')
    min_width = properties.get('min-width')
    sections = properties.get('sections', [])

    if not sections:
        return "> [!CAUTION]\n> **Layout Error:** At least one section is required"

    if not isinstance(sections, list):
        return "> [!CAUTION]\n> **Layout Error:** 'sections' must be a list"

    # Build flex container style
    flex_direction = orientation
    container_style = f"display: flex; flex-direction: {flex_direction};"

    # Add gap if specified
    if gap and gap != '0':
        # Parse gap size
        gap_value, gap_unit = parse_size(gap)
        if gap_value != 'auto':
            container_style += f" gap: {gap_value}{gap_unit};"

    # Add border if specified
    if border:
        border_css = parse_border(border)
        if border_css:
            container_style += f" border: {border_css};"

    # Add padding if specified
    if padding:
        padding_value, padding_unit = parse_size(str(padding))
        if padding_value != 'auto':
            container_style += f" padding: {padding_value}{padding_unit};"

    # Add background if specified
    if background:
        container_style += f" background: {background};"

    # Add overflow if specified
    if overflow:
        container_style += f" overflow: {overflow};"

    # Add separate overflow-x and overflow-y if specified (overrides overflow)
    if overflow_x:
        container_style += f" overflow-x: {overflow_x};"
    if overflow_y:
        container_style += f" overflow-y: {overflow_y};"

    # Add dimension constraints
    if max_height:
        mh_value, mh_unit = parse_size(str(max_height))
        if mh_value != 'auto':
            container_style += f" max-height: {mh_value}{mh_unit};"

    if max_width:
        mw_value, mw_unit = parse_size(str(max_width))
        if mw_value != 'auto':
            container_style += f" max-width: {mw_value}{mw_unit};"

    if min_height:
        mih_value, mih_unit = parse_size(str(min_height))
        if mih_value != 'auto':
            container_style += f" min-height: {mih_value}{mih_unit};"

    if min_width:
        miw_value, miw_unit = parse_size(str(min_width))
        if miw_value != 'auto':
            container_style += f" min-width: {miw_value}{miw_unit};"

    # Process each section
    section_html_parts = []

    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            section_html_parts.append(
                f'<div style="flex: 1 1 auto;">'
                f'<p><em>Invalid section {i+1}: must be a dictionary</em></p>'
                f'</div>'
            )
            continue

        # Get section size (default to auto)
        size = section.get('size', 'auto')
        flex_value = size_to_flex(str(size))

        # Build section style
        section_style = f"flex: {flex_value};"

        # Add per-section styling
        section_border = section.get('border')
        if section_border:
            border_css = parse_border(section_border)
            if border_css:
                section_style += f" border: {border_css};"

        section_padding = section.get('padding')
        if section_padding:
            padding_value, padding_unit = parse_size(str(section_padding))
            if padding_value != 'auto':
                section_style += f" padding: {padding_value}{padding_unit};"

        section_background = section.get('background')
        if section_background:
            section_style += f" background: {section_background};"

        # Add section overflow
        section_overflow = section.get('overflow')
        if section_overflow:
            section_style += f" overflow: {section_overflow};"

        section_overflow_x = section.get('overflow-x')
        if section_overflow_x:
            section_style += f" overflow-x: {section_overflow_x};"

        section_overflow_y = section.get('overflow-y')
        if section_overflow_y:
            section_style += f" overflow-y: {section_overflow_y};"

        # Add section dimension constraints
        section_max_height = section.get('max-height')
        if section_max_height:
            smh_value, smh_unit = parse_size(str(section_max_height))
            if smh_value != 'auto':
                section_style += f" max-height: {smh_value}{smh_unit};"

        section_max_width = section.get('max-width')
        if section_max_width:
            smw_value, smw_unit = parse_size(str(section_max_width))
            if smw_value != 'auto':
                section_style += f" max-width: {smw_value}{smw_unit};"

        section_min_height = section.get('min-height')
        if section_min_height:
            smih_value, smih_unit = parse_size(str(section_min_height))
            if smih_value != 'auto':
                section_style += f" min-height: {smih_value}{smih_unit};"

        section_min_width = section.get('min-width')
        if section_min_width:
            smiw_value, smiw_unit = parse_size(str(section_min_width))
            if smiw_value != 'auto':
                section_style += f" min-width: {smiw_value}{smiw_unit};"

        # Get embedded content
        embed = section.get('embed')
        if not embed:
            section_html_parts.append(
                f'<div style="{section_style}">'
                f'<p><em>Section {i+1}: No embed specified</em></p>'
                f'</div>'
            )
            continue

        if not isinstance(embed, dict):
            section_html_parts.append(
                f'<div style="{section_style}">'
                f'<p><em>Section {i+1}: embed must be a dictionary</em></p>'
                f'</div>'
            )
            continue

        # Process the embedded content based on type
        embed_type = embed.get('type', '').replace('embed.', '')

        if embed_type == 'file':
            embedded_content = process_file_embed(embed, current_file_dir, processing_stack, context)
        elif embed_type in ('toc', 'table_of_contents'):
            # Generate TOC - check if source file is specified
            source = embed.get('source')
            if source:
                # Generate TOC from specified file
                embedded_content = generate_table_of_contents('', source_file=source, current_file_dir=current_file_dir)
            else:
                # No source specified - cannot generate TOC in layout context
                embedded_content = "> [!CAUTION]\n> **TOC Error:** 'source' property is required for TOC in layouts. Specify which file to generate TOC from."
        else:
            embedded_content = f"> [!CAUTION]\n> **Layout Error:** Unknown embed type in section {i+1}: '{embed_type}'"

        # Wrap in section div
        section_html = f'<div style="{section_style}">\n\n{embedded_content}\n\n</div>'
        section_html_parts.append(section_html)

    # Combine all sections into container
    sections_html = '\n'.join(section_html_parts)

    layout_html = f'<div style="{container_style}">\n{sections_html}\n</div>'

    return layout_html


def validate_layout_sizes(sections: List[Dict]) -> Optional[str]:
    """
    Validate that section sizes make sense.

    Args:
        sections: List of section dictionaries

    Returns:
        Warning message if validation fails, None otherwise
    """
    total_percent = 0
    has_auto = False
    has_pixel = False

    for section in sections:
        if not isinstance(section, dict):
            continue

        size = section.get('size', 'auto')
        value, unit = parse_size(str(size))

        if value == 'auto':
            has_auto = True
        elif unit == '%':
            try:
                total_percent += float(value)
            except ValueError:
                pass
        elif unit == 'px':
            has_pixel = True

    # Warn if percentages exceed 100%
    if total_percent > 100 and not has_auto:
        return f"> [!WARNING]\n> Layout warning: Total percentage ({total_percent}%) exceeds 100%"

    # Warn if mixing pixels with percentages without auto
    if has_pixel and total_percent > 0 and not has_auto:
        return "> [!WARNING]\n> Layout warning: Mixing pixels and percentages without 'auto' may not work as expected"

    return None
