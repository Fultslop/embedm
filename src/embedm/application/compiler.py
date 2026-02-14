from embedm.domain.plan_node import PlanNode

from .embedm_context import EmbedmContext


def compile(plan_node: PlanNode, context: EmbedmContext) -> str:
    raise NotImplementedError("todo")
