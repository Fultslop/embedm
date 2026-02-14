from dataclasses import dataclass


@dataclass
class Directive:
    type: str
    options: dict[str, str]
