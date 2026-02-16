from dataclasses import dataclass, field

from .directive import Directive
from .span import Span

# Define the allowed types
Fragment = str | Span | Directive


@dataclass
class Document:
    file_name: str
    fragments: list[Fragment] = field(default_factory=list)
