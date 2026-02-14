"""Validation phase - check limits, file existence, and dependencies."""

import os
from typing import List

from .models import Limits, ValidationError, ValidationResult, EmbedDirective
from .discovery import (
    discover_files,
    discover_all_embeds,
    build_dependency_graph,
    detect_cycles,
    calculate_max_depth
)


def validate_all(source_path: str, limits: Limits, sandbox=None) -> ValidationResult:
    """
    Comprehensive validation phase - discover and validate everything before execution.

    Args:
        source_path: File or directory to process
        limits: Processing limits

    Returns:
        ValidationResult with errors, warnings, and discovered embeds
    """
    result = ValidationResult()

    # Record sandbox info for display
    if sandbox and sandbox.enabled:
        from .sandbox import format_sandbox_info
        result.sandbox_info = format_sandbox_info(sandbox)
    elif sandbox and not sandbox.enabled:
        result.sandbox_info = "disabled (--no-sandbox)"

    # Step 1: Discover all files to process
    files = discover_files(source_path)

    if not files:
        result.errors.append(ValidationError(
            file_path=source_path,
            line_number=None,
            error_type='no_files',
            message=f"No markdown files found: {source_path}",
            severity='error'
        ))
        return result

    result.files_to_process = files

    # Step 2: Validate individual file sizes and discover embeds
    for file_path in files:
        # Check if file exists (should always be true, but defensive check)
        if not os.path.exists(file_path):
            result.errors.append(ValidationError(
                file_path=file_path,
                line_number=None,
                error_type='missing_file',
                message=f"File not found: {file_path}",
                severity='error'
            ))
            continue

        # Check file size limit
        file_size = os.path.getsize(file_path)
        if limits.max_file_size > 0 and file_size > limits.max_file_size:
            result.errors.append(ValidationError(
                file_path=file_path,
                line_number=None,
                error_type='limit_exceeded',
                message=f"File size {Limits.format_size(file_size)} exceeds limit {Limits.format_size(limits.max_file_size)}",
                severity='error'
            ))
            # Skip discovering embeds in this file since it exceeds size limit
            continue

    # Step 3: Discover all embeds across all valid files
    result.embeds_discovered = discover_all_embeds(result.files_to_process)

    # Step 3.5: Validate embed properties
    validate_embed_properties(result)

    # Step 4: Check embed count per file
    embed_counts = {}
    for embed in result.embeds_discovered:
        embed_counts[embed.file_path] = embed_counts.get(embed.file_path, 0) + 1

    for file_path, count in embed_counts.items():
        if limits.max_embeds_per_file > 0 and count > limits.max_embeds_per_file:
            result.errors.append(ValidationError(
                file_path=file_path,
                line_number=None,
                error_type='limit_exceeded',
                message=f"File has {count} embeds, limit is {limits.max_embeds_per_file}",
                severity='error'
            ))

    # Step 5: Validate all source files exist
    for embed in result.embeds_discovered:
        # Only file embeds have source files
        if embed.embed_type == 'file':
            if not embed.source_file:
                result.errors.append(ValidationError(
                    file_path=embed.file_path,
                    line_number=embed.line_number,
                    error_type='missing_property',
                    message="'source' property is required for file embeds",
                    severity='error'
                ))
                continue

            if not os.path.exists(embed.source_file):
                # Get relative path for better error message
                try:
                    rel_path = os.path.relpath(embed.source_file, os.path.dirname(embed.file_path))
                except ValueError:
                    rel_path = embed.source_file

                result.errors.append(ValidationError(
                    file_path=embed.file_path,
                    line_number=embed.line_number,
                    error_type='missing_file',
                    message=f"Source file not found: {rel_path}",
                    severity='error'
                ))
                continue

            # Check sandbox access
            if sandbox and sandbox.enabled:
                from .sandbox import check_sandbox as _check_sandbox
                violation = _check_sandbox(embed.source_file, sandbox)
                if violation:
                    result.errors.append(ValidationError(
                        file_path=embed.file_path,
                        line_number=embed.line_number,
                        error_type='sandbox_violation',
                        message=violation,
                        severity='error'
                    ))
                    continue

            # Check if source file exceeds size limit
            if os.path.isfile(embed.source_file):
                source_size = os.path.getsize(embed.source_file)
                if limits.max_file_size > 0 and source_size > limits.max_file_size:
                    result.warnings.append(ValidationError(
                        file_path=embed.file_path,
                        line_number=embed.line_number,
                        error_type='limit_warning',
                        message=f"Source file {os.path.basename(embed.source_file)} size {Limits.format_size(source_size)} exceeds limit",
                        severity='warning'
                    ))

            # Validate regions if specified
            region = embed.properties.get('region')
            if region:
                validate_region(embed, result)

            # Validate symbols if specified
            symbol = embed.properties.get('symbol')
            if symbol:
                validate_symbol(embed, result)

    # Step 6: Build dependency graph and check for cycles
    result.dependency_graph = build_dependency_graph(result.embeds_discovered)

    cycles = detect_cycles(result.dependency_graph)
    for cycle in cycles:
        # Format cycle as A -> B -> C -> A
        cycle_str = " -> ".join(os.path.basename(f) for f in cycle)
        result.errors.append(ValidationError(
            file_path=cycle[0],
            line_number=None,
            error_type='circular_dependency',
            message=f"Circular dependency detected: {cycle_str}",
            severity='error'
        ))

    # Step 7: Check recursion depth
    if result.dependency_graph:
        max_depth = calculate_max_depth(result.dependency_graph)

        if limits.max_recursion > 0 and max_depth > limits.max_recursion:
            result.errors.append(ValidationError(
                file_path=None,
                line_number=None,
                error_type='limit_exceeded',
                message=f"Dependency depth {max_depth} exceeds recursion limit {limits.max_recursion}",
                severity='error'
            ))
        elif limits.max_recursion > 0 and max_depth >= limits.max_recursion - 1:
            result.warnings.append(ValidationError(
                file_path=None,
                line_number=None,
                error_type='limit_warning',
                message=f"Dependency depth {max_depth} is approaching recursion limit {limits.max_recursion}",
                severity='warning'
            ))

    # Step 8: Estimate embedded text sizes
    validate_embed_text_sizes(result, limits)

    return result


def validate_region(embed: EmbedDirective, result: ValidationResult):
    """
    Validate that a region specification is valid.

    Args:
        embed: Embed directive with region property
        result: ValidationResult to append errors to
    """
    import re
    from .extraction import extract_lines, extract_region

    region = embed.properties.get('region')
    if not region or not embed.source_file or not os.path.exists(embed.source_file):
        return

    with open(embed.source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try to extract the region
    result_data = extract_lines(content, region)
    if not result_data:
        result_data = extract_region(content, region)

    if not result_data:
        result.errors.append(ValidationError(
            file_path=embed.file_path,
            line_number=embed.line_number,
            error_type='invalid_region',
            message=f"Region '{region}' not found in {os.path.basename(embed.source_file)}",
            severity='error'
        ))


def validate_symbol(embed: EmbedDirective, result: ValidationResult):
    """
    Validate that a symbol specification is valid.

    Checks that the language is supported and the symbol exists in the source file.

    Args:
        embed: Embed directive with symbol property
        result: ValidationResult to append errors to
    """
    from .symbols import get_language_config, extract_symbol

    symbol = embed.properties.get('symbol')
    if not symbol or not embed.source_file or not os.path.exists(embed.source_file):
        return

    # Check language support
    config = get_language_config(embed.source_file)
    if config is None:
        file_ext = os.path.splitext(embed.source_file)[1]
        result.errors.append(ValidationError(
            file_path=embed.file_path,
            line_number=embed.line_number,
            error_type='unsupported_language',
            message=f"Symbol extraction not supported for '{file_ext}' files",
            severity='error'
        ))
        return

    # Check symbol exists
    with open(embed.source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    result_data = extract_symbol(content, symbol, embed.source_file)
    if not result_data:
        result.errors.append(ValidationError(
            file_path=embed.file_path,
            line_number=embed.line_number,
            error_type='invalid_symbol',
            message=f"Symbol '{symbol}' not found in {os.path.basename(embed.source_file)}",
            severity='error'
        ))


def validate_embed_text_sizes(result: ValidationResult, limits: Limits):
    """
    Estimate and validate embedded text sizes.

    Args:
        result: ValidationResult to append warnings to
        limits: Processing limits
    """
    if limits.max_embed_text <= 0:
        return

    for embed in result.embeds_discovered:
        # Only check file embeds
        if embed.embed_type != 'file':
            continue

        if not embed.source_file or not os.path.exists(embed.source_file):
            continue

        # Get file size as rough estimate
        try:
            source_size = os.path.getsize(embed.source_file)

            # If embedding a region, we can't easily estimate without executing
            # So only check full file embeds
            if 'region' not in embed.properties:
                if source_size > limits.max_embed_text:
                    result.warnings.append(ValidationError(
                        file_path=embed.file_path,
                        line_number=embed.line_number,
                        error_type='limit_warning',
                        message=f"Embedded file {os.path.basename(embed.source_file)} size {Limits.format_size(source_size)} exceeds embed text limit {Limits.format_size(limits.max_embed_text)}",
                        severity='warning'
                    ))
        except OSError:
            pass


def validate_embed_properties(result: ValidationResult):
    """
    Validate that embed properties are recognized by their plugins.

    Checks each embed's properties against the plugin's valid_properties list
    and adds warnings for unknown properties (excluding 'type' and 'comment').

    Args:
        result: ValidationResult to append warnings to
    """
    from .registry import get_default_registry
    from .phases import ProcessingPhase

    registry = get_default_registry()

    for embed in result.embeds_discovered:
        # Get the plugin for this embed type
        # Try EMBED phase first (most common)
        plugin = registry.get_plugin(embed.embed_type, ProcessingPhase.EMBED)

        if not plugin:
            # Try POST_PROCESS phase (for TOC)
            plugin = registry.get_plugin(embed.embed_type, ProcessingPhase.POST_PROCESS)

        if not plugin:
            # Unknown embed type - will be caught elsewhere
            continue

        # Get valid properties from plugin
        valid_props = set(plugin.valid_properties)

        # Add universal properties
        valid_props.add('type')
        valid_props.add('comment')

        # Check each property in the embed
        for prop_name in embed.properties.keys():
            if prop_name not in valid_props:
                # Found unknown property - add warning
                valid_list = ', '.join(sorted(plugin.valid_properties))
                result.warnings.append(ValidationError(
                    file_path=embed.file_path,
                    line_number=embed.line_number,
                    error_type='unknown_property',
                    message=f"Unknown property '{prop_name}' for embed type '{embed.embed_type}'. Valid properties: {valid_list}",
                    severity='warning'
                ))
