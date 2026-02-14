
from .directive import Directive
from .span import Span

# Define the allowed types
Fragment = str | Span | Directive

class Document:
    def __init__(self, file_name: str, fragments: list[Fragment]):
        self.file_name = file_name
        self.fragments = fragments
