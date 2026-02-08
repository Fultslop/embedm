"""
Example Plugin for EmbedM
=========================

This example demonstrates how to create a custom embed plugin that
reverses the content of text files.

Usage in markdown:
    ```yaml
    type: embed.reverse
    source: file.txt
    uppercase: true  # Optional: convert to uppercase
    ```
"""

from typing import List, Dict, Set, Optional
import sys
import os

# Add src to path for standalone execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext


class ReversePlugin(EmbedPlugin):
    """Plugin that reverses file content (example)."""

    @property
    def name(self) -> str:
        return "reverse"

    @property
    def embed_types(self) -> List[str]:
        return ["reverse"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        return [ProcessingPhase.EMBED]

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        # Get source file
        source = properties.get('source')
        if not source:
            return self.format_error("Missing Property", "source is required")

        # Resolve path
        file_path = self.resolve_path(source, current_file_dir)

        # Check file exists
        error = self.check_file_exists(file_path)
        if error:
            return error

        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return self.format_error("Read Error", str(e))

        # Reverse content
        reversed_content = content[::-1]

        # Optional: uppercase
        if properties.get('uppercase'):
            reversed_content = reversed_content.upper()

        # Wrap in code block
        from embedm.plugin import wrap_in_code_block
        return wrap_in_code_block(reversed_content, file_path=file_path)


if __name__ == '__main__':
    # Demo usage
    import tempfile

    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello, World!")
        test_file = f.name

    try:
        # Create plugin instance
        plugin = ReversePlugin()

        # Process the embed
        properties = {'source': test_file}
        current_dir = os.path.dirname(test_file)
        processing_stack = set()

        result = plugin.process(properties, current_dir, processing_stack)

        print("Plugin name:", plugin.name)
        print("Embed types:", plugin.embed_types)
        print("Phases:", plugin.phases)
        print("\nProcessed output:")
        print(result)

        # Test with uppercase option
        properties_upper = {'source': test_file, 'uppercase': True}
        result_upper = plugin.process(properties_upper, current_dir, processing_stack)

        print("\nWith uppercase option:")
        print(result_upper)

    finally:
        # Clean up
        os.unlink(test_file)
