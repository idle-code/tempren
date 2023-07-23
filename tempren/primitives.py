import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

tag_name_regex = re.compile(r"^[_a-z][0-9_a-z]*$", re.IGNORECASE)


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


class PathGenerator(ABC):
    @abstractmethod
    def generate(self, file: File) -> Path:
        raise NotImplementedError()


class TagName(str):
    def __new__(cls, name: str) -> "TagName":
        if not tag_name_regex.match(name):
            raise ValueError(f"Invalid name: {repr(name)}")
        return super().__new__(cls, name)  # type: ignore


class CategoryName(TagName):
    pass


@dataclass
class QualifiedTagName:
    name: TagName
    # TODO: if this is meant to be a genuinely qualified name, the category should be specified:
    category: Optional[CategoryName] = None

    def __init__(
        self,
        name: Union[TagName, str],
        category: Optional[Union[CategoryName, str]] = None,
    ) -> None:
        if not isinstance(name, TagName):
            name = TagName(name)
        if category is not None and not isinstance(category, CategoryName):
            category = CategoryName(category)
        self.name = name
        self.category = category

    def __str__(self) -> str:
        if self.category:
            return f"{self.category}.{self.name}"
        return f"{self.name}"


@dataclass
class Location:
    line: int
    column: int
    length: int

    def __str__(self) -> str:
        if self.length == 1:
            return f"line {self.line}:{self.column}"
        return f"line {self.line}:{self.column}-{self.column + self.length}"


class Tag(ABC):
    require_context: Optional[bool] = None
    """Determine if tag requires context

    When set to True - an error is reported if no context is provided.
    When set to False - an error is reported if context is provided.
    When set to None - context is optional (tag decides what to do with it).
    """

    def configure(self):
        """Initialize tag instance with configuration options provided by the user"""
        pass

    @abstractmethod
    def process(self, file: File, context: Optional[str]) -> Any:
        """Execute tag logic on a single file/context"""
        raise NotImplementedError()


class TagFactory(ABC):
    @property
    @abstractmethod
    def tag_name(self) -> TagName:
        """Name of produced tags"""

    @property
    @abstractmethod
    def configuration_signature(self) -> str:
        """Configuration arguments"""

    @property
    @abstractmethod
    def short_description(self) -> str:
        """Short (one-line) tag description"""

    @property
    @abstractmethod
    def long_description(self) -> Optional[str]:
        """Longer tag documentation"""

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Tag:
        """Creates tag from provided configuration arguments"""
