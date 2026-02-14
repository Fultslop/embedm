"""
Mermaid Plugin for EmbedM
==========================

Converts simplified arrow-delimited text into Mermaid flowchart diagrams.

Instead of writing full Mermaid syntax, you can describe a flowchart with a
simple arrow-delimited string and let the plugin generate the diagram code.

Supported delimiters: → (unicode arrow), -> (ascii arrow), , (comma)

Usage in markdown:
    ```yaml embedm
    type: mermaid
    input: User's Markdown → Parser → Registry Dispatcher → Plugin.process() → Output
    ```

    ```yaml embedm
    type: mermaid
    chart: flowchart RL
    input: Output -> Processing -> Input
    ```
"""

import re
from typing import Dict, Set, Optional, List

from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from embedm.resolver import ProcessingContext

# Supported chart types
VALID_CHART_TYPES = {"flowchart", "graph"}
VALID_DIRECTIONS = {"LR", "RL", "TB", "BT", "TD"}

# Delimiter pattern: → or -> or , (with optional surrounding whitespace)
DELIMITER_PATTERN = re.compile(r'\s*(?:→|->|,)\s*')


class MermaidPlugin(EmbedPlugin):
    """Plugin that converts arrow-delimited text into Mermaid flowchart diagrams.

    Handles embed types:
    - embed.mermaid: Generate Mermaid flowchart from simplified input
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "mermaid"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["mermaid"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        """Processing phases when this plugin runs."""
        return [ProcessingPhase.EMBED]

    @property
    def valid_properties(self) -> List[str]:
        """Valid properties for mermaid embeds."""
        return [
            "input",  # Required: arrow-delimited node text
            "chart",  # Optional: chart type and direction (default: flowchart LR)
            "title",  # Optional: title displayed above the diagram
        ]

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        """Process mermaid embed.

        Args:
            properties: YAML properties (input, chart, title)
            current_file_dir: Directory containing the markdown file
            processing_stack: Set of files being processed (cycle detection)
            context: Processing context with limits

        Returns:
            Mermaid code block or error message
        """
        input_text = properties.get('input')
        if not input_text:
            return self.format_error("Mermaid Error", "'input' property is required")

        # Parse chart type and direction
        chart = properties.get('chart', 'flowchart LR')
        error = self._validate_chart(chart)
        if error:
            return error

        # Split input into node labels
        nodes = DELIMITER_PATTERN.split(str(input_text))
        nodes = [n.strip() for n in nodes if n.strip()]

        if len(nodes) < 2:
            return self.format_error(
                "Mermaid Error",
                "At least 2 nodes are required. Separate nodes with →, ->, or comma."
            )

        # Build mermaid diagram
        lines = [chart]

        # Node definitions
        for i, label in enumerate(nodes, 1):
            lines.append(f'  n_{i}["{label}"]')

        # Connections
        for i in range(len(nodes) - 1):
            lines.append(f'  n_{i + 1} --> n_{i + 2}')

        content = '\n'.join(lines)
        result = f'```mermaid\n{content}\n```'

        # Wrap with title if provided
        title = properties.get('title')
        if title:
            result = f'**{title}**\n\n{result}'

        return result

    def _validate_chart(self, chart: str) -> Optional[str]:
        """Validate chart type string.

        Args:
            chart: Chart specification (e.g., 'flowchart LR')

        Returns:
            None if valid, error string if invalid
        """
        parts = chart.strip().split()
        if len(parts) != 2:
            return self.format_error(
                "Mermaid Error",
                f"Invalid chart format: '{chart}'. Expected format: 'flowchart LR'"
            )

        chart_type, direction = parts
        if chart_type.lower() not in VALID_CHART_TYPES:
            return self.format_error(
                "Mermaid Error",
                f"Unknown chart type: '{chart_type}'. Supported: {', '.join(sorted(VALID_CHART_TYPES))}"
            )

        if direction.upper() not in VALID_DIRECTIONS:
            return self.format_error(
                "Mermaid Error",
                f"Unknown direction: '{direction}'. Supported: {', '.join(sorted(VALID_DIRECTIONS))}"
            )

        return None
