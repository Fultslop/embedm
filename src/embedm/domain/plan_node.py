from __future__ import annotations  # to deal with the children property

from dataclasses import dataclass

from embedm.domain.status_level import Status

from .directive import Directive
from .document import Document


@dataclass
class PlanNode:
    directive: Directive
    status: list[Status]
    document: Document | None = None
    children: list[PlanNode] | None = None
