import glob
import os
from collections import OrderedDict
from collections.abc import Callable
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path

from embedm.domain.status_level import Status, StatusLevel

from .infrastructure_resources import str_resources


class WriteMode(Enum):
    OVERWRITE = 1
    CREATE_NEW = 2


class FileState(Enum):
    NOT_IN_CACHE = 1
    LOADED = 2
    UNLOADED = 3


class FileCache:
    """
    LRU file cache with memory management and path access control.

    Allowed paths may contain wildcards (* and **) for pattern matching.
    """

    def __init__(
        self,
        max_file_size: int,
        memory_limit: int,
        allowed_paths: list[str],
        write_mode: WriteMode = WriteMode.CREATE_NEW,
        max_embed_size: int = 0,
        on_event: Callable[[str, str], None] | None = None,
    ):
        assert memory_limit > max_file_size, (
            f"memory_limit ({memory_limit}) must be greater than max_file_size ({max_file_size})"
        )
        self.max_file_size = max_file_size
        self.memory_limit = memory_limit
        self.allowed_paths = allowed_paths
        self.write_mode = write_mode
        self.max_embed_size = max_embed_size
        self._on_event = on_event
        self._cache: OrderedDict[str, str | None] = OrderedDict()
        self._memory_in_use = 0

    def validate(self, path: str) -> list[Status]:
        """
        Check if the file at path exists, is within the max file size,
        and matches the allowed paths. Pure check with no side effects.
        Skips filesystem checks if already in cache.
        """
        if path in self._cache:
            return []

        errors: list[Status] = []

        if not _is_path_allowed(path, self.allowed_paths):
            errors.append(Status(StatusLevel.FATAL, f"path is not in allowed paths: '{path}'"))
            return errors

        if not os.path.isfile(path):
            errors.append(Status(StatusLevel.ERROR, f"file does not exist: '{path}'"))
            return errors

        file_size = os.path.getsize(path)
        if file_size > self.max_file_size:
            errors.append(
                Status(
                    StatusLevel.ERROR,
                    f"file exceeds max size ({file_size} > {self.max_file_size}): '{path}'",
                )
            )

        return errors

    def get_file(self, path: str) -> tuple[str | None, list[Status]]:
        """
        Return cached file content or validate and load from disk.

        Validates the path before loading. On validation failure, returns
        None and the validation errors.
        Moves the entry to the front of the cache on access.
        If loading would exceed memory_limit, evicts least recently used
        loaded entries until there is room.
        """
        # return cached content if loaded
        if path in self._cache and self._cache[path] is not None:
            self._cache.move_to_end(path, last=False)
            if self._on_event:
                self._on_event(path, "hit")
            return self._cache[path], []

        # validate if not yet in cache
        if path not in self._cache:
            errors = self.validate(path)
            if errors:
                return None, errors

        # load from disk
        content = Path(path).read_text(encoding="utf-8")
        self._make_room(len(content))
        self._cache[path] = content
        self._cache.move_to_end(path, last=False)
        self._memory_in_use += len(content)
        if self._on_event:
            self._on_event(path, "miss")

        return content, []

    def write(self, content: str, path: str) -> tuple[str | None, list[Status]]:
        """
        Write content to a file at the given path.

        The path must match the allowed paths. If a file already exists,
        behavior depends on write_mode:
        - OVERWRITE: replaces the existing file.
        - CREATE_NEW: creates file_name.N.extension where N is the next
          available number.

        Returns the actual file path written to and any errors.
        The written file is added to the cache.
        """
        if not _is_path_allowed(path, self.allowed_paths):
            return None, [Status(StatusLevel.FATAL, str_resources.err_path_not_allowed.format(path=path))]

        actual_path = path
        if os.path.isfile(path) and self.write_mode == WriteMode.CREATE_NEW:
            actual_path = _find_next_available_path(path)

        Path(actual_path).write_text(content, encoding="utf-8")

        self._make_room(len(content))
        self._cache[actual_path] = content
        self._cache.move_to_end(actual_path, last=False)
        self._memory_in_use += len(content)

        return actual_path, []

    def get_file_state(self, path: str) -> FileState:
        """Check whether the path exists in the cache and its load state."""
        if path not in self._cache:
            return FileState.NOT_IN_CACHE
        if self._cache[path] is not None:
            return FileState.LOADED
        return FileState.UNLOADED

    def get_files(self, pattern: str) -> tuple[list[str], list[Status]]:
        """
        Return file paths matching the pattern.

        Valid patterns include full paths, relative paths to the current
        working directory, or wildcards (*) and (**) for recursive searches.
        The resolved paths must match the allowed paths.
        """
        matched = glob.glob(pattern, recursive=True)
        files: list[str] = []
        errors: list[Status] = []

        for file_path in matched:
            resolved = str(Path(file_path).resolve())
            if _is_path_allowed(resolved, self.allowed_paths):
                files.append(resolved)
            else:
                errors.append(Status(StatusLevel.ERROR, f"matched file is not in allowed paths: '{resolved}'"))

        return files, errors

    def _make_room(self, needed: int) -> None:
        """Evict least recently used loaded entries until there is room."""
        while self._memory_in_use + needed > self.memory_limit:
            evicted = self._evict_lru()
            if not evicted:
                break

    def _evict_lru(self) -> bool:
        """Evict the least recently used loaded entry. Returns False if nothing to evict."""
        for path in reversed(self._cache):
            content = self._cache[path]
            if content is not None:
                self._memory_in_use -= len(content)
                self._cache[path] = None
                if self._on_event:
                    self._on_event(path, "eviction")
                return True
        return False


def _is_path_allowed(path: str, allowed_paths: list[str]) -> bool:
    """Check if a path matches any of the allowed path patterns."""
    resolved = Path(path).resolve()
    for allowed in allowed_paths:
        allowed_resolved = Path(allowed).resolve()
        # directory boundary match (exact match or subdirectory)
        try:
            resolved.relative_to(allowed_resolved)
            return True
        except ValueError:
            pass
        # wildcard match
        if fnmatch(str(resolved), str(allowed_resolved)):
            return True
    return False


def _find_next_available_path(path: str) -> str:
    """Find the next available numbered path: file.N.ext."""
    p = Path(path)
    stem = p.stem
    suffix = p.suffix
    parent = p.parent
    counter = 0
    while True:
        candidate = parent / f"{stem}.{counter}{suffix}"
        if not candidate.exists():
            return str(candidate)
        counter += 1
