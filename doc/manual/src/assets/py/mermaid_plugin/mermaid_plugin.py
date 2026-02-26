import re
from typing import Any

from embedm.plugins.api import Directive, PlanNode, PluginBase, PluginConfiguration, Status, StatusLevel, NormalizationResult

INPUT_KEY = "input"

DELIMITER_PATTERN = re.compile(r'\s*(?:→|->|,)\s*')

class MermaidPlugin(PluginBase):
    name = "mermaid"
    api_version = 1
    directive_type = "mermaid"

    def validate_directive(
        self, 
        directive: Directive, 
        _configuration: PluginConfiguration | None = None
    ) -> list[Status]:
        
        input_str = directive.options.get(INPUT_KEY)
        
        if input_str is None:
            return [Status(StatusLevel.ERROR,'Mermaid plugin is missing  Directive option "Input"')]

        return []

    def normalize_input(
            self,
            directive: Directive,
            content: str,
            _plugin_config: PluginConfiguration | None = None,
        ) -> NormalizationResult[Any]:

        input_text = directive.options.get(INPUT_KEY)

        # Split input into node labels
        nodes = DELIMITER_PATTERN.split(str(input_text))
        nodes = [n.strip() for n in nodes if n.strip()]

        if len(nodes) < 2:
            return NormalizationResult(errors=
                [Status(StatusLevel.ERROR,"Mermaid error At least 2 nodes are required. Separate nodes with →, ->, or comma.")])

        return NormalizationResult(normalized_data=nodes)

    def transform(self, plan_node: PlanNode, parent_document, context=None):
        nodes = plan_node.normalized_data

        # Build mermaid diagram
        lines = ['flowchart LR']

        # Node definitions
        for i, label in enumerate(nodes, 1):
            lines.append(f'  n_{i}["{label}"]')

        # Connections
        for i in range(len(nodes) - 1):
            lines.append(f'  n_{i + 1} --> n_{i + 2}')

        content = '\n'.join(lines)
        result = f'```mermaid\n{content}\n```'

        # Wrap with title if provided
        title = 'Mermaid chart'
        if title:
            result = f'**{title}**\n\n{result}'

        return result