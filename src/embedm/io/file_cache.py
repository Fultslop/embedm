class FileCache:
    def __init__(self, max_file_size: int, memory_limit: int):
        self.max_file_size = max_file_size
        self.memory_limit = memory_limit

    def get_file_size(self, path: str) -> int:
        raise NotImplementedError("todo")

    def get_file(self, path: str) -> str:
        raise NotImplementedError("todo")

    def write(self, content: str, path: str) -> None:
        raise NotImplementedError("todo")
