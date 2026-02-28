from __future__ import annotations

from collections.abc import Sequence

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import StatusLevel
from embedm.plugins.plugin_base import PluginBase


class _StubPlugin(PluginBase):
    name = "stub"
    directive_type = "stub"
    deprecated_option_names = {
        "show_link": ["link"],
        "show_line_range": ["line_numbers_range"],
    }

    def transform(self, plan_node: PlanNode, parent_document: Sequence[Fragment], context=None) -> str:
        return ""


# --- remap_deprecated_options ---


def test_remap_deprecated_options_remaps_in_place():
    plugin = _StubPlugin()
    directive = Directive(type="stub", options={"link": "True"})

    plugin.remap_deprecated_options(directive)

    assert "show_link" in directive.options
    assert "link" not in directive.options
    assert directive.options["show_link"] == "True"


def test_remap_deprecated_options_returns_warning_status():
    plugin = _StubPlugin()
    directive = Directive(type="stub", options={"link": "True"})

    warnings = plugin.remap_deprecated_options(directive)

    assert len(warnings) == 1
    assert warnings[0].level == StatusLevel.WARNING
    assert "link" in warnings[0].description
    assert "show_link" in warnings[0].description


def test_remap_deprecated_options_no_warning_if_absent():
    plugin = _StubPlugin()
    directive = Directive(type="stub", options={})

    warnings = plugin.remap_deprecated_options(directive)

    assert warnings == []
    assert directive.options == {}


def test_remap_deprecated_options_canonical_name_passes_through_unchanged():
    plugin = _StubPlugin()
    directive = Directive(type="stub", options={"show_link": "True"})

    warnings = plugin.remap_deprecated_options(directive)

    assert warnings == []
    assert directive.options == {"show_link": "True"}


def test_remap_deprecated_options_multiple_deprecated_names_each_get_warning():
    plugin = _StubPlugin()
    directive = Directive(type="stub", options={"link": "True", "line_numbers_range": "True"})

    warnings = plugin.remap_deprecated_options(directive)

    assert len(warnings) == 2
    assert "show_link" in directive.options
    assert "show_line_range" in directive.options
    assert "link" not in directive.options
    assert "line_numbers_range" not in directive.options


def test_remap_deprecated_options_no_deprecated_names_declared():
    class _Bare(PluginBase):
        name = "bare"
        directive_type = "bare"

        def transform(self, plan_node, parent_document, context=None) -> str:
            return ""

    plugin = _Bare()
    directive = Directive(type="bare", options={"some_option": "value"})

    warnings = plugin.remap_deprecated_options(directive)

    assert warnings == []
    assert directive.options == {"some_option": "value"}
