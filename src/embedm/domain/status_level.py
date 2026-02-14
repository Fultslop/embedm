from dataclasses import dataclass
from enum import Enum


class StatusLevel(Enum):
    OK = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

@dataclass
class Status:
    level: StatusLevel
    description: str
