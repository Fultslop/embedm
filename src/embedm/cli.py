"""Command-line interface for embedm."""

import sys
import os

from .resolver import resolve_content, resolve_table_of_contents


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage:\n  embedm <file.md>\n  embedm <file.md> <output.md>\n  embedm <source_dir> <output_dir>")
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


if __name__ == '__main__':
    main()
