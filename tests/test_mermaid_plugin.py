"""Tests for the mermaid plugin."""

import pytest
from embedm_plugins.mermaid_plugin import MermaidPlugin


class TestMermaidPluginInterface:
    """Test plugin metadata and interface."""

    def test_plugin_name(self):
        plugin = MermaidPlugin()
        assert plugin.name == "mermaid"

    def test_plugin_embed_types(self):
        plugin = MermaidPlugin()
        assert plugin.embed_types == ["mermaid"]

    def test_plugin_valid_properties(self):
        plugin = MermaidPlugin()
        assert "input" in plugin.valid_properties
        assert "chart" in plugin.valid_properties
        assert "title" in plugin.valid_properties


class TestMermaidProcessing:
    """Test mermaid flowchart generation."""

    def test_basic_flowchart_with_unicode_arrows(self):
        """Test basic flowchart with → delimiter."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B → C'},
            '/tmp', set()
        )

        assert '```mermaid' in result
        assert 'flowchart LR' in result
        assert 'n_1["A"]' in result
        assert 'n_2["B"]' in result
        assert 'n_3["C"]' in result
        assert 'n_1 --> n_2' in result
        assert 'n_2 --> n_3' in result
        assert result.endswith('```')

    def test_basic_flowchart_with_ascii_arrows(self):
        """Test basic flowchart with -> delimiter."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'Input -> Processing -> Output'},
            '/tmp', set()
        )

        assert 'n_1["Input"]' in result
        assert 'n_2["Processing"]' in result
        assert 'n_3["Output"]' in result
        assert 'n_1 --> n_2' in result
        assert 'n_2 --> n_3' in result

    def test_basic_flowchart_with_commas(self):
        """Test basic flowchart with comma delimiter."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'Step 1, Step 2, Step 3'},
            '/tmp', set()
        )

        assert 'n_1["Step 1"]' in result
        assert 'n_2["Step 2"]' in result
        assert 'n_3["Step 3"]' in result

    def test_mixed_delimiters(self):
        """Test that mixed delimiters all work."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B -> C, D'},
            '/tmp', set()
        )

        assert 'n_1["A"]' in result
        assert 'n_2["B"]' in result
        assert 'n_3["C"]' in result
        assert 'n_4["D"]' in result
        assert 'n_1 --> n_2' in result
        assert 'n_2 --> n_3' in result
        assert 'n_3 --> n_4' in result

    def test_custom_chart_direction(self):
        """Test custom chart type and direction."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B', 'chart': 'flowchart RL'},
            '/tmp', set()
        )

        assert 'flowchart RL' in result

    def test_graph_keyword(self):
        """Test 'graph' chart type."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B', 'chart': 'graph TB'},
            '/tmp', set()
        )

        assert 'graph TB' in result

    def test_all_directions(self):
        """Test all valid directions."""
        plugin = MermaidPlugin()
        for direction in ['LR', 'RL', 'TB', 'BT', 'TD']:
            result = plugin.process(
                {'input': 'A → B', 'chart': f'flowchart {direction}'},
                '/tmp', set()
            )
            assert f'flowchart {direction}' in result

    def test_title_property(self):
        """Test optional title wrapping."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B', 'title': 'My Diagram'},
            '/tmp', set()
        )

        assert result.startswith('**My Diagram**')
        assert '```mermaid' in result

    def test_no_title(self):
        """Test output without title."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B'},
            '/tmp', set()
        )

        assert result.startswith('```mermaid')

    def test_realistic_pipeline(self):
        """Test with a realistic pipeline description."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': "User's Markdown → Parser → Registry Dispatcher → Plugin.process() → Output"},
            '/tmp', set()
        )

        assert 'n_1["User\'s Markdown"]' in result
        assert 'n_2["Parser"]' in result
        assert 'n_3["Registry Dispatcher"]' in result
        assert 'n_4["Plugin.process()"]' in result
        assert 'n_5["Output"]' in result
        assert 'n_1 --> n_2' in result
        assert 'n_4 --> n_5' in result


class TestMermaidErrorHandling:
    """Test error cases."""

    def test_missing_input(self):
        """Test error when input property is missing."""
        plugin = MermaidPlugin()
        result = plugin.process({}, '/tmp', set())

        assert '[!CAUTION]' in result
        assert "'input' property is required" in result

    def test_single_node(self):
        """Test error when only one node provided."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'JustOneNode'},
            '/tmp', set()
        )

        assert '[!CAUTION]' in result
        assert 'At least 2 nodes' in result

    def test_invalid_chart_format(self):
        """Test error for malformed chart property."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B', 'chart': 'invalid'},
            '/tmp', set()
        )

        assert '[!CAUTION]' in result
        assert 'Invalid chart format' in result

    def test_invalid_chart_type(self):
        """Test error for unknown chart type."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B', 'chart': 'sequence LR'},
            '/tmp', set()
        )

        assert '[!CAUTION]' in result
        assert "Unknown chart type: 'sequence'" in result

    def test_invalid_direction(self):
        """Test error for unknown direction."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': 'A → B', 'chart': 'flowchart XX'},
            '/tmp', set()
        )

        assert '[!CAUTION]' in result
        assert "Unknown direction: 'XX'" in result

    def test_empty_input(self):
        """Test error when input is empty string."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': ''},
            '/tmp', set()
        )

        assert '[!CAUTION]' in result

    def test_only_delimiters(self):
        """Test error when input is only delimiters."""
        plugin = MermaidPlugin()
        result = plugin.process(
            {'input': '→ → →'},
            '/tmp', set()
        )

        assert '[!CAUTION]' in result
        assert 'At least 2 nodes' in result
