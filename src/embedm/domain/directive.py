from dataclasses import dataclass, field


@dataclass
class Directive:
    type: str
    options: dict[str, str] = field(default_factory=dict)
