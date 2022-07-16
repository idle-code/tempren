from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path, PosixPath
from typing import Any


@dataclass
class File:
    input_directory: Path
    relative_path: Path

    @classmethod
    def from_path(cls, path_representation: str) -> "File":
        path = Path(path_representation)
        return File(path.parent, Path(path.name))

    @property
    def absolute_path(self) -> Path:
        return self.input_directory / self.relative_path

    def __init__(self, input_directory: Path, relative_path: Path):
        assert input_directory.is_absolute()
        assert not relative_path.is_absolute()
        self.input_directory = input_directory
        self.relative_path = relative_path

    def __str__(self):
        return str(self.relative_path)

    def __repr__(self):
        return repr(str(self))


class InvalidFilenameError(Exception):
    generated_name: str

    def __init__(self, invalid_name: str):
        super().__init__(f"Invalid name: '{invalid_name}'")
        self.generated_name = invalid_name


class PathGenerator(ABC):
    @abstractmethod
    def generate(self, file: File) -> Path:
        raise NotImplementedError()


class ExpressionEvaluationError(Exception):
    expression: str

    @property
    def message(self) -> str:
        return str(self.__cause__)

    def __init__(self, expression: str):
        self.expression = expression


class TemplateEvaluationError(Exception):
    file: File
    template: str
    expression: str
    message: str

    def __init__(self, file: File, template: str, expression: str, message: str):
        self.file = file
        self.template = template
        self.expression = expression
        self.message = message


_evaluation_locals = {"PosixPath": PosixPath}


def evaluate_expression(python_expression: str) -> Any:
    try:
        evaluation_result = eval(python_expression, {}, _evaluation_locals)
        return evaluation_result
    except Exception as exc:
        raise ExpressionEvaluationError(python_expression) from exc
