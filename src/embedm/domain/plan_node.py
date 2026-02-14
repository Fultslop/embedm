from __future__ import annotations  # to deal with the children property

from dataclasses import dataclass
from enum import Enum

from .directive import Directive
from .document import Document


class PlanNodeStatus(Enum):
    OK = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

@dataclass
class PlanNode:
    directive: Directive
    status: PlanNodeStatus
    status_description: str
    document: Document
    children: list[PlanNode]
