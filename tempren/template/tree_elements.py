from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, List, Mapping, Optional


@dataclass
class Location:
    line: int
    column: int
    length: int

    def __str__(self) -> str:
        if self.length == 1:
            return f"line {self.line}:{self.column}"
        return f"line {self.line}:{self.column}-{self.column + self.length}"


class PatternElement(ABC):
    @abstractmethod
    def process(self, path: Path) -> Any:
        raise NotImplementedError()


@dataclass
class RawText(PatternElement):
    location: Location = field(init=False, compare=False)
    text: str

    def process(self, path: Path) -> str:
        return self.text


@dataclass
class Pattern(PatternElement):
    sub_elements: List[PatternElement] = field(default_factory=list)

    def process(self, path: Path) -> str:
        return "".join(
            map(
                lambda se: Pattern._convert_tag_value(se.process(path)),
                self.sub_elements,
            )
        )

    @staticmethod
    def _convert_tag_value(tag_value) -> str:
        if isinstance(tag_value, str):
            return tag_value
        return repr(tag_value)


@dataclass
class TagPlaceholder(PatternElement):
    location: Location = field(init=False, compare=False)
    tag_name: str
    context: Optional[Pattern] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.tag_name) < 1:
            raise ValueError(f"Invalid tag name: ${repr(self.tag_name)}")

    def process(self, path: Path) -> str:
        raise NotImplementedError(
            "TagInvocation shouldn't be present in bound tag tree"
        )


class Tag(ABC):
    require_context: Optional[bool] = None
    # TODO: works_on_directories: bool = False
    # TODO: stateful: bool = False  # Warn if no sorting expression is specified

    def configure(self, *args, **kwargs):
        pass

    @abstractmethod
    def process(self, path: Path, context: Optional[str]) -> Any:
        raise NotImplementedError()


TagFactory = Callable[..., Tag]


@dataclass
class TagInstance(PatternElement):
    tag: Tag
    context: Optional[Pattern] = None

    def process(self, path: Path) -> Any:
        context_str = self.context.process(path) if self.context else None
        return self.tag.process(path, context_str)
