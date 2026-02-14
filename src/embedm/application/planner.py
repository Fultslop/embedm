from embedm.domain.plan_node import PlanNode

from .embedm_context import EmbedmContext


def create_plan(content: str, context: EmbedmContext) -> PlanNode:
    """
    1) Go through the content, break it up into a document.
    2) If no error gather all directives
    """
    raise NotImplementedError("todo")
