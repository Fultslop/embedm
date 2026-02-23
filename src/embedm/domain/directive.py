from dataclasses import dataclass, field


@dataclass
class Directive:
    type: str
    # source file, may be None if a directive does not use an input file
    # eg ToC
    source: str = ""
    options: dict[str, str] = field(default_factory=dict)
    # directory of the file that contains this directive (for relative link computation)
    base_dir: str = ""
