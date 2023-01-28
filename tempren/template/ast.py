from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional

from tempren.path_generator import File


@dataclass
class Location:
    line: int
    column: int
    length: int

    def __str__(self) -> str:
        if self.length == 1:
            return f"line {self.line}:{self.column}"
        return f"line {self.line}:{self.column}-{self.column + self.length}"


@dataclass
class TagName:
    location: Location = field(init=False, compare=False)
    name: str
    category: Optional[str] = None

    def __post_init__(self):
        if len(self.name) < 1:
            raise ValueError(f"Invalid tag name: ${repr(self.name)}")
        if self.category is not None and len(self.category) < 1:
            raise ValueError(f"Invalid category name: ${repr(self.category)}")

    def __str__(self) -> str:
        if self.category:
            return f"{self.category}.{self.name}"
        return f"{self.name}"


class PatternElement(ABC):
    """Represents element of template pattern"""

    location: Location = field(init=False, compare=False)

    @abstractmethod
    def process(self, file: File) -> Any:
        raise NotImplementedError()


@dataclass
class RawText(PatternElement):
    """Represents constant text (non-tag) part of the template"""

    text: str

    def process(self, file: File) -> str:
        return self.text


@dataclass
class Pattern(PatternElement):
    """Represents pattern tree - a chain of text/tag invocations"""

    sub_elements: List[PatternElement] = field(default_factory=list)
    source_representation: Optional[str] = field(
        init=False, default=None, compare=False
    )

    def process(self, file: File) -> str:
        """Recursively renders pattern as a string"""
        return "".join(
            map(
                lambda se: str(se.process(file)),
                self.sub_elements,
            )
        )

    def process_as_expression(self, file: File) -> str:
        """Recursively renders pattern as an expression string

        In expression string, values returned by the tags are converted using `repr`
        rather than `str` to obtain valid python value representation.
        """
        return "".join(
            map(
                lambda se: Pattern._convert_to_representation(se, file),
                self.sub_elements,
            )
        )

    @staticmethod
    def _convert_to_representation(element: PatternElement, file: File) -> str:
        """Renders value returned by tag invocation as a string representation (as to be used in evaluated
        expressions)"""
        tag_value = element.process(file)
        if isinstance(element, TagInstance):
            return repr(tag_value)
        return str(tag_value)


@dataclass
class TagPlaceholder(PatternElement):
    """Represents unbound tag"""

    tag_name: TagName
    context: Optional[Pattern] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def process(self, file: File) -> str:
        raise NotImplementedError(
            "TagPlaceholder shouldn't be present in bound tag tree"
        )


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


class FileNotSupportedError(Exception):
    """Tag cannot extract value due to invalid file type"""

    pass


class MissingMetadataError(Exception):
    """Tag cannot extract value due to missing metadata"""

    pass


@dataclass
class TagInstance(PatternElement):
    """Represents a tag bound to the implementation"""

    tag: Tag
    context: Optional[Pattern] = None

    def process(self, file: File) -> Any:
        context_str = self.context.process(file) if self.context else None
        try:
            return self.tag.process(file, context_str)
        except MissingMetadataError:
            return ""
