"""Command-line interface for embedm."""

import sys
import os
import argparse
import time

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for Windows console
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from .models import Limits, ProcessingStats
from .validation import validate_all
from .resolver import resolve_content, resolve_table_of_contents, ProcessingContext


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='EmbedM - Embed files, code snippets, and generate TOCs in Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  embedm input.md                           # Creates input.compiled.md
  embedm input.md output.md                 # Creates output.md
  embedm source_dir/ output_dir/            # Process directory

  # Override limits:
  embedm input.md --max-file-size 5MB
  embedm input.md --max-recursion 10 --max-embeds 200
  embedm input.md --max-output-size 20MB --max-embed-text 5KB

  # Disable limits (use 0):
  embedm input.md --max-recursion 0         # Unlimited recursion

Size formats: 1024, 1KB, 1K, 1MB, 1M, 1GB, 1G
        """
    )

    # Positional arguments
    parser.add_argument(
        'source',
        help='Source markdown file or directory'
    )
    parser.add_argument(
        'output',
        nargs='?',
        help='Output file or directory (optional for single file)'
    )

    # Limit override flags
    limits_group = parser.add_argument_group('processing limits')

    limits_group.add_argument(
        '--max-file-size',
        type=str,
        default='1MB',
        metavar='SIZE',
        help='Maximum input file size (default: 1MB, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-recursion',
        type=int,
        default=8,
        metavar='N',
        help='Maximum recursion depth (default: 8, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-embeds',
        type=int,
        default=100,
        metavar='N',
        help='Maximum embeds per file (default: 100, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-output-size',
        type=str,
        default='10MB',
        metavar='SIZE',
        help='Maximum output file size (default: 10MB, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-embed-text',
        type=str,
        default='2KB',
        metavar='SIZE',
        help='Maximum embedded text length (default: 2KB, use 0 for unlimited)'
    )

    # Other flags
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate only, do not process files'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force processing even with validation errors (warnings will be embedded in output)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    return parser.parse_args()


def create_limits_from_args(args) -> Limits:
    """Create Limits object from parsed arguments."""
    return Limits(
        max_file_size=Limits.parse_size(args.max_file_size),
        max_recursion=args.max_recursion,
        max_embeds_per_file=args.max_embeds,
        max_output_size=Limits.parse_size(args.max_output_size),
        max_embed_text=Limits.parse_size(args.max_embed_text)
    )


def process_files(validation_result, output_path: str, limits: Limits, verbose: bool = False, force: bool = False) -> ProcessingStats:
    """
    Execute the processing phase - resolve embeds and write output files.

    Args:
        validation_result: Validated embeds and files
        output_path: Output file or directory (or None for auto-generated)
        limits: Processing limits
        verbose: Verbose output flag
        force: Force processing with embedded warnings

    Returns:
        ProcessingStats with processing metrics
    """
    stats = ProcessingStats()
    start_time = time.time()

    print("\n⚙️  Processing Phase")
    print("━" * 60)

    files = validation_result.files_to_process

    # Determine if we're in directory mode
    is_dir_mode = len(files) > 1 or (output_path and os.path.isdir(output_path))

    # Create processing context with limits (only if force mode is enabled)
    context = ProcessingContext(limits if force else None)

    if is_dir_mode:
        # Directory mode
        if not output_path:
            print("❌ Error: Output directory required when processing multiple files")
            sys.exit(1)

        absolute_output = os.path.abspath(output_path)
        os.makedirs(absolute_output, exist_ok=True)

        for file_path in files:
            # First pass: resolve file embeds with limit checking
            final_content = resolve_content(file_path, context=context)

            # Second pass: resolve table of contents
            final_content = resolve_table_of_contents(final_content, source_file_path=file_path)

            # Check output size limit
            output_size = len(final_content.encode('utf-8'))
            if limits.max_output_size > 0 and output_size > limits.max_output_size:
                print(f"⚠️  Warning: {os.path.basename(file_path)} output size {Limits.format_size(output_size)} exceeds limit")

            output_file = os.path.join(absolute_output, os.path.basename(file_path))
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_content)

            stats.files_processed += 1
            stats.total_output_size += output_size

            print(f"  ✅ {os.path.basename(file_path)} → {os.path.basename(absolute_output)}{os.sep}{os.path.basename(output_file)}")

    else:
        # Single file mode
        file_path = files[0]

        # First pass: resolve file embeds with limit checking
        final_content = resolve_content(file_path, context=context)

        # Second pass: resolve table of contents
        final_content = resolve_table_of_contents(final_content, source_file_path=file_path)

        # Check output size limit
        output_size = len(final_content.encode('utf-8'))
        if limits.max_output_size > 0 and output_size > limits.max_output_size:
            print(f"⚠️  Warning: Output size {Limits.format_size(output_size)} exceeds limit {Limits.format_size(limits.max_output_size)}")

        # Determine output path
        if output_path:
            target = os.path.abspath(output_path)
        else:
            target = file_path.replace('.md', '.compiled.md')

        with open(target, 'w', encoding='utf-8') as f:
            f.write(final_content)

        stats.files_processed = 1
        stats.total_output_size = output_size

        print(f"  ✅ {os.path.basename(file_path)} → {os.path.basename(target)}")

    stats.duration_seconds = time.time() - start_time
    return stats


def main():
    """Main CLI entry point with new pipeline architecture."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Create limits from arguments
        limits = create_limits_from_args(args)

        # PHASE 1: Validation
        validation = validate_all(args.source, limits)

        # PHASE 2: Report Results
        print(validation.format_report(verbose=args.verbose))

        # Show how to override limits if there are limit-related errors
        if validation.has_errors():
            limit_errors = [e for e in validation.errors if e.error_type in ('limit_exceeded', 'limit_warning')]
            if limit_errors:
                print("\nTip: Override limits with flags like:")
                print("  --max-file-size 5MB --max-recursion 10 --max-embeds 200")

            # Exit unless --force is specified
            if not args.force:
                sys.exit(1)
            else:
                print("\n⚠️  --force enabled: Processing will continue with errors.")
                print("    Warnings will be embedded in the compiled output.\n")

        # Exit if dry-run
        if args.dry_run:
            print("\n✅ Dry run complete - no files were modified")
            sys.exit(0)

        # PHASE 3: Execute Processing (always run if no errors, or if --force is set)
        if not validation.has_errors() or args.force:
            stats = process_files(validation, args.output, limits, args.verbose, args.force)
            print(f"\n{stats.format_summary()}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as err:
        print(f"\n❌ Critical Error: {err}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
