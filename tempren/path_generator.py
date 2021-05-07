from abc import ABC, abstractmethod
from pathlib import Path


class File:
    path: Path
    # TODO: add handle for caching open(path) handle - typing.IO?

    def __init__(self, path: Path):
        self.path = path

    def __str__(self):
        return f"File({repr(str(self.path))})"


class PathGenerator(ABC):
    start_directory: Path

    def __init__(self, start_directory: Path):
        assert start_directory.is_dir()
        self.start_directory = start_directory

    @abstractmethod
    def reset(self):
        raise NotImplementedError()

    @abstractmethod
    def generate(self, file: File) -> Path:
        raise NotImplementedError()
