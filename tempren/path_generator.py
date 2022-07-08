from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TextIO


@dataclass
class File:
    absolute_path: Path
    relative_path: Path

    def __init__(self, path: Path, input_directory: Optional[Path] = None):
        if input_directory is None:
            assert path.is_absolute()
            self.absolute_path = path
            self.relative_path = path.relative_to(path.parent)
        else:
            assert not path.is_absolute() and input_directory.is_dir()
            self.absolute_path = input_directory / path
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
