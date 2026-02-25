# todo
# transform with max_depth set
# transform with add_slugs

from embedm.domain.directive import Directive
from embedm.domain.plan_node import PlanNode
from embedm_plugins.toc_plugin import ToCPlugin
from embedm_plugins.toc.toc_transformer import ADD_SLUGS_KEY, MAX_DEPTH_KEY


def test_plugin_validate_directive_greenpath():
    plugin = ToCPlugin()
    status_list = plugin.validate_directive(directive=Directive(type="toc"))

    assert status_list is not None
    assert len(status_list) == 0


def test_plugin_validate_directive_greenpath_all_params():
    plugin = ToCPlugin()

    directive = Directive(type="toc", options={MAX_DEPTH_KEY: "1", ADD_SLUGS_KEY: "True"})

    status_list = plugin.validate_directive(directive)

    assert status_list is not None
    assert len(status_list) == 0


def test_plugin_validate_directive_red_path():
    plugin = ToCPlugin()

    directive = Directive(type="toc", options={MAX_DEPTH_KEY: "foo", ADD_SLUGS_KEY: "bad"})

    status_list = plugin.validate_directive(directive)

    assert status_list is not None
    assert len(status_list) == 2


def test_plugin_transform_document_is_none():
    plugin = ToCPlugin()
    plan_node = PlanNode(Directive(type="toc"), [])
    output = plugin.transform(plan_node, parent_document=None)

    assert output == ""


def test_plugin_transform_document_is_empty():
    plugin = ToCPlugin()
    plan_node = PlanNode(Directive(type="toc"), [])
    output = plugin.transform(plan_node, parent_document=[])

    assert output == ""


def test_plugin_transform_document_with_default_options():
    plugin = ToCPlugin()
    plan_node = PlanNode(Directive(type="toc"), [])
    output = plugin.transform(plan_node, parent_document=["## header"])

    assert output == "  - header\n"


def test_plugin_transform_document_with_max_depth():
    plugin = ToCPlugin()
    options = {MAX_DEPTH_KEY: "2"}
    plan_node = PlanNode(Directive(type="toc", options=options), [])
    output = plugin.transform(plan_node, parent_document=["## header\n### header"])

    assert output == "  - header\n"


def test_plugin_transform_document_with_add_slugs():
    plugin = ToCPlugin()
    options = {ADD_SLUGS_KEY: "True"}  # "True" is the string produced by the parser (str(True))
    plan_node = PlanNode(Directive(type="toc", options=options), [])
    output = plugin.transform(plan_node, parent_document=["## header"])

    assert output == "  - [header](#header)\n"


# The ToC should only generate headings after its own directive
def test_plugin_transform_document_expect_headings_after_toc():
    plugin = ToCPlugin()
    toc_directive = Directive(type="toc")
    plan_node = PlanNode(toc_directive, [])
    parent_document = ["# title", toc_directive, "## header"]
    output = plugin.transform(plan_node, parent_document)

    assert output == "  - header\n"
