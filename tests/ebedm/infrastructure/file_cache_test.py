import os
from pathlib import Path

from embedm.infrastructure.file_cache import FileCache, FileState, WriteMode


# --- validate: happy path ---


def test_validate_existing_file_on_allowed_path(tmp_path: Path):
    test_file = tmp_path / "readme.md"
    test_file.write_text("hello")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    errors = cache.validate(str(test_file))

    assert errors == []


def test_validate_skips_checks_when_already_cached(tmp_path: Path):
    test_file = tmp_path / "readme.md"
    test_file.write_text("hello")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    # load file into cache
    content, errors = cache.get_file(str(test_file))
    assert errors == []

    # delete the file from disk
    os.remove(str(test_file))

    # validate should still pass because it's in cache
    errors = cache.validate(str(test_file))
    assert errors == []


# --- get_file: happy path ---


def test_get_file_loads_from_disk(tmp_path: Path):
    test_file = tmp_path / "readme.md"
    test_file.write_text("hello world")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    content, errors = cache.get_file(str(test_file))

    assert errors == []
    assert content == "hello world"


def test_get_file_returns_cached_content_even_if_file_changed(tmp_path: Path):
    """Files are assumed not to change between planning and execution (see architecture doc)."""
    test_file = tmp_path / "readme.md"
    test_file.write_text("hello world")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    # first load
    content_1, _ = cache.get_file(str(test_file))

    # modify the file on disk
    test_file.write_text("changed content")

    # second load returns cached content — undefined behavior per architecture doc
    content_2, _ = cache.get_file(str(test_file))

    assert content_1 == content_2 == "hello world"


def test_get_file_evicts_lru_when_memory_full(tmp_path: Path):
    file_a = tmp_path / "a.md"
    file_b = tmp_path / "b.md"
    file_c = tmp_path / "c.md"
    file_a.write_text("aaaa")  # 4 bytes
    file_b.write_text("bbbb")  # 4 bytes
    file_c.write_text("cccc")  # 4 bytes

    # memory limit fits only 2 files
    cache = FileCache(
        max_file_size=1024,
        memory_limit=8,
        allowed_paths=[str(tmp_path)],
    )

    cache.get_file(str(file_a))
    cache.get_file(str(file_b))

    # loading c should evict a (least recently used)
    content_c, errors = cache.get_file(str(file_c))

    assert errors == []
    assert content_c == "cccc"
    assert cache.get_file_state(str(file_a)) == FileState.UNLOADED
    assert cache.get_file_state(str(file_b)) == FileState.LOADED
    assert cache.get_file_state(str(file_c)) == FileState.LOADED


# --- get_file_state: happy path ---


def test_get_file_state_not_in_cache(tmp_path: Path):
    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    assert cache.get_file_state(str(tmp_path / "unknown.md")) == FileState.NOT_IN_CACHE


def test_get_file_state_loaded(tmp_path: Path):
    test_file = tmp_path / "readme.md"
    test_file.write_text("hello")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    cache.get_file(str(test_file))

    assert cache.get_file_state(str(test_file)) == FileState.LOADED


# --- write: happy path ---


def test_write_new_file(tmp_path: Path):
    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    target = str(tmp_path / "output.md")

    written_path, errors = cache.write("compiled output", target)

    assert errors == []
    assert written_path == target
    assert Path(target).read_text() == "compiled output"


def test_write_overwrite_existing(tmp_path: Path):
    existing = tmp_path / "output.md"
    existing.write_text("old content")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
        write_mode=WriteMode.OVERWRITE,
    )

    written_path, errors = cache.write("new content", str(existing))

    assert errors == []
    assert written_path == str(existing)
    assert existing.read_text() == "new content"


def test_write_create_new_when_exists(tmp_path: Path):
    existing = tmp_path / "output.md"
    existing.write_text("original")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
        write_mode=WriteMode.CREATE_NEW,
    )

    written_path, errors = cache.write("new version", str(existing))

    assert errors == []
    # original file untouched
    assert existing.read_text() == "original"
    # new file created as output.0.md
    expected_new = str(tmp_path / "output.0.md")
    assert written_path == expected_new
    assert Path(expected_new).read_text() == "new version"


def test_write_adds_to_cache(tmp_path: Path):
    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )
    target = str(tmp_path / "output.md")

    cache.write("compiled output", target)

    assert cache.get_file_state(target) == FileState.LOADED


# --- get_files: happy path ---


def test_get_files_with_wildcard(tmp_path: Path):
    (tmp_path / "doc1.md").write_text("one")
    (tmp_path / "doc2.md").write_text("two")
    (tmp_path / "notes.txt").write_text("three")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )

    files, errors = cache.get_files(str(tmp_path / "*.md"))

    assert errors == []
    assert len(files) == 2
    assert str(tmp_path / "doc1.md") in files
    assert str(tmp_path / "doc2.md") in files


def test_get_files_recursive_wildcard(tmp_path: Path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "root.md").write_text("root")
    (sub / "nested.md").write_text("nested")

    cache = FileCache(
        max_file_size=1024,
        memory_limit=4096,
        allowed_paths=[str(tmp_path)],
    )

    files, errors = cache.get_files(str(tmp_path / "**" / "*.md"))

    assert errors == []
    assert len(files) == 2
    assert str(tmp_path / "root.md") in files
    assert str(sub / "nested.md") in files
