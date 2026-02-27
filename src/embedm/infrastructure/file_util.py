from pathlib import Path


def to_relative(path: str) -> str:
    """Return path relative to CWD as a POSIX string, or the original path if not under CWD."""
    try:
        return Path(path).relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path


def apply_line_endings(text: str, line_endings: str) -> str:
    """Normalise output line endings. 'crlf' converts LF→CRLF; 'lf' is a no-op."""
    if line_endings == "crlf":
        return text.replace("\n", "\r\n")
    return text


def glob_base(pattern: str) -> Path:
    """Return the directory prefix of a glob pattern: all parts before the first wildcard."""
    base: list[str] = []
    for part in Path(pattern).parts:
        if "*" in part:
            break
        base.append(part)
    return Path(*base) if base else Path(".")


def extract_base_dir(input_path: str) -> Path:
    """Extract the base directory from a directory input or glob pattern."""
    return glob_base(input_path).resolve() if "*" in input_path else Path(input_path).resolve()


def expand_directory_input(input_path: str, pattern: str = "*.md") -> list[str]:
    """Expand a directory or glob pattern to a sorted list of matching files."""
    if "**" in input_path:
        return sorted(str(p) for p in glob_base(input_path).rglob(pattern))
    if "*" in input_path:
        return sorted(str(p) for p in glob_base(input_path).glob(pattern))
    return sorted(str(p) for p in Path(input_path).glob(pattern))
