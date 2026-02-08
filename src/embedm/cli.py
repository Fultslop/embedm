"""Command-line interface for embedm."""

import sys
import os
import argparse
import time

# Fix Windows console encoding for emojis (but not during testing)
if sys.platform == 'win32' and 'pytest' not in sys.modules:
    try:
        # Try to set UTF-8 encoding for Windows console
        import io
        if hasattr(sys.stdout, 'buffer') and hasattr(sys.stderr, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from .models import Limits, ProcessingStats
from .validation import validate_all
from .resolver import ProcessingContext
from .phases import PhaseProcessor


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
        default=None,
        metavar='SIZE',
        help='Maximum input file size (default: 1MB or from config, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-recursion',
        type=int,
        default=None,
        metavar='N',
        help='Maximum recursion depth (default: 8 or from config, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-embeds',
        type=int,
        default=None,
        metavar='N',
        help='Maximum embeds per file (default: 100 or from config, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-output-size',
        type=str,
        default=None,
        metavar='SIZE',
        help='Maximum output file size (default: 10MB or from config, use 0 for unlimited)'
    )

    limits_group.add_argument(
        '--max-embed-text',
        type=str,
        default=None,
        metavar='SIZE',
        help='Maximum embedded text length (default: 2KB or from config, use 0 for unlimited)'
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


def create_limits(args, config=None) -> Limits:
    """Create Limits object with precedence: CLI > config > defaults.

    Args:
        args: Parsed command-line arguments
        config: Optional loaded config file (EmbedMConfig)

    Returns:
        Limits object with merged values
    """
    from .config import EmbedMConfig

    # Helper to get value with precedence
    def get_value(cli_val, config_val, default_val):
        # CLI arg was explicitly set (not None)
        if cli_val is not None:
            return cli_val
        # Config has value
        if config and config_val is not None:
            return config_val
        # Use default
        return default_val

    return Limits(
        max_file_size=Limits.parse_size(
            get_value(args.max_file_size,
                     config.max_file_size if config else None,
                     "1MB")
        ),
        max_recursion=get_value(
            args.max_recursion,
            config.max_recursion if config else None,
            8
        ),
        max_embeds_per_file=get_value(
            args.max_embeds,
            config.max_embeds_per_file if config else None,
            100
        ),
        max_output_size=Limits.parse_size(
            get_value(args.max_output_size,
                     config.max_output_size if config else None,
                     "10MB")
        ),
        max_embed_text=Limits.parse_size(
            get_value(args.max_embed_text,
                     config.max_embed_text if config else None,
                     "2KB")
        )
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
            # Process all phases
            processor = PhaseProcessor(context=context)
            final_content = processor.process_all_phases(file_path)

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

        # Process all phases
        processor = PhaseProcessor(context=context)
        final_content = processor.process_all_phases(file_path)

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
    """Main CLI entry point with config file support."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Load config file if processing a directory
        config = None
        config_path = None
        if os.path.isdir(args.source):
            from .config import find_config_file, load_config, prompt_create_config, ConfigValidationError

            config_path = find_config_file(args.source)

            if config_path:
                try:
                    config = load_config(config_path)
                    print(f"📄 Using config: {os.path.relpath(config_path)}\n")
                except ConfigValidationError as e:
                    print(f"❌ Config file error: {e}")
                    sys.exit(1)
            else:
                # Prompt to create config (Option B: continue if declined)
                if prompt_create_config(args.source):
                    config_path = os.path.join(args.source, 'embedm_config.yaml')
                    try:
                        config = load_config(config_path)
                        print(f"✅ Created config: {os.path.relpath(config_path)}\n")
                    except ConfigValidationError as e:
                        print(f"⚠️  Warning: Created config has errors: {e}")
                        config = None

        # Create limits with precedence: CLI > config > defaults
        limits = create_limits(args, config)

        # Determine output path with config fallback
        output_path = args.output
        if not output_path and config and config.output_directory:
            # Make config output directory relative to config file location
            config_dir = os.path.dirname(config_path)
            output_path = os.path.join(config_dir, config.output_directory)
            # Create the directory if it came from config and source is a directory
            # This ensures directory mode is detected correctly in process_files()
            if os.path.isdir(args.source):
                os.makedirs(output_path, exist_ok=True)

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
            stats = process_files(validation, output_path, limits, args.verbose, args.force)
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
