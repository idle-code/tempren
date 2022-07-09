from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TextIO, Union


class File:
    input_directory: Path
    absolute_path: Path

    @classmethod
    def from_path(cls, path: Union[Path, str]) -> "File":
        path = Path(path)
        return File(path.parent, path)

    @property
    def relative_path(self) -> Path:
        return self.absolute_path.relative_to(self.input_directory)

    def __init__(self, input_directory: Path, absolute_path: Path):
        assert input_directory.is_absolute()
        assert absolute_path.is_absolute()
        # TODO: use assert absolute_path.is_relative_to(input_directory) with Python 3.9
        assert str(absolute_path).startswith(str(input_directory))
        self.input_directory = input_directory
        self.absolute_path = absolute_path

    def __str__(self):
        return f"File({repr(str(self.relative_path))})"


class PathGenerator(ABC):
    @abstractmethod
    def reset(self):
        raise NotImplementedError()

    @abstractmethod
    def generate(self, file: File) -> Path:
        raise NotImplementedError()
