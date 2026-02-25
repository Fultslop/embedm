from pathlib import Path


def to_relative(path: str) -> str:
    """Return path relative to CWD as a POSIX string, or the original path if not under CWD."""
    try:
        return Path(path).relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path
