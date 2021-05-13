from abc import ABC, abstractmethod
from pathlib import Path


class File:
    relative_path: Path
    # TODO: add handle for caching open(path) handle - typing.IO?

    def __init__(self, path: Path):
        assert not path.is_absolute()
        self.relative_path = path

    def __str__(self):
        return f"File({repr(str(self.relative_path))})"


class PathGenerator(ABC):
    @abstractmethod
    def reset(self):
        raise NotImplementedError()

    @abstractmethod
    def generate(self, file: File) -> Path:
        raise NotImplementedError()
