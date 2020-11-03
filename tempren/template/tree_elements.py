from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, List, Mapping, Optional


class PatternElement(ABC):
    @abstractmethod
    def process(self, path: Path) -> str:
        raise NotImplementedError()


@dataclass(frozen=True)
class RawText(PatternElement):
    text: str

    def process(self, path: Path) -> str:
        return self.text


@dataclass(frozen=True)
class Pattern(PatternElement):
    sub_elements: List[PatternElement] = field(default_factory=list)

    def process(self, path: Path) -> str:
        return "".join(map(lambda se: se.process(path), self.sub_elements))


# class TagFactory(Protocol):
#     def __call__(self, *args, context_present: bool = False, **kwargs) -> "Tag":
#         ...


class Tag(ABC):
    require_context: Optional[bool] = None

    @abstractmethod
    def configure(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def process(self, path: Path, context: Optional[str]) -> str:
        raise NotImplementedError()


@dataclass
class TagInstance(PatternElement):
    tag: Tag
    context: Optional[Pattern] = None

    def process(self, path: Path) -> str:
        context_str = self.context.process(path) if self.context else None
        return self.tag.process(path, context_str)


TagFactory = Callable[..., Tag]


@dataclass(frozen=True)
class TagPlaceholder(PatternElement):
    tag_name: str
    context: Optional[Pattern] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.tag_name) < 1:
            raise ValueError(f"Invalid tag name: ${repr(self.tag_name)}")

    def process(self, path: Path) -> str:
        raise NotImplementedError(
            "TagInvocation shouldn't be present in concrete tag tree"
        )
