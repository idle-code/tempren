from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, List, Mapping, Optional, Protocol


class PatternElement(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass(frozen=True)
class RawText(PatternElement):
    text: str

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class Pattern(PatternElement):
    sub_elements: List[PatternElement] = field(default_factory=list)

    def __str__(self) -> str:
        return "".join(map(str, self.sub_elements))


# class TagFactory(Protocol):
#     def __call__(self, *args, context_present: bool = False, **kwargs) -> "Tag":
#         ...


class Tag(PatternElement, ABC):
    pass


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

    def __str__(self) -> str:
        raise NotImplementedError(
            "TagInvocation shouldn't be present in concrete tag tree"
        )
