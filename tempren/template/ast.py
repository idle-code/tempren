from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional

from tempren.exceptions import MissingMetadataError
from tempren.primitives import File, Location, QualifiedTagName, Tag


class PatternElement(ABC):
    """Represents element of template pattern"""

    @abstractmethod
    def process(self, file: File) -> Any:
        raise NotImplementedError()


@dataclass
class RawText(PatternElement):
    """Represents constant text (non-tag) part of the template"""

    location: Location = field(init=False, compare=False, default=Location(-1, -1, -1))
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

    location: Location = field(init=False, compare=False)
    tag_name: QualifiedTagName
    context: Optional[Pattern] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def process(self, file: File) -> Any:
        raise NotImplementedError(
            "TagPlaceholder shouldn't be present in bound tag tree"
        )


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
