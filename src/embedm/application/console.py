from embedm.domain.plan_node import PlanNode


def present_title() -> None:
    print("Ebedm version 0.5")

def present_plan(root: PlanNode, is_force_set: bool) -> bool:
    raise NotImplementedError("todo")

def present_arg_errors(errors: list[str]) -> None:
    raise NotImplementedError("todo")
