from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from tempren.exceptions import FileMetadataError
from tempren.primitives import File, Location, Pattern, QualifiedTagName, Tag
from tempren.template.evaluation_context import EvaluationContext


class PatternElement(ABC):
    """Represents element of template pattern"""

    @abstractmethod
    def process(self, file: File, evaluation: EvaluationContext) -> Any:
        raise NotImplementedError()


@dataclass
class RawText(PatternElement):
    """Represents constant text (non-tag) part of the template"""

    location: Location = field(init=False, compare=False, default=Location(-1, -1, -1))
    text: str

    def process(self, file: File, evaluation: EvaluationContext) -> str:
        return self.text


@dataclass
class PatternElementSequence(PatternElement, Pattern):
    """Represents pattern tree - a chain of text/tag invocations"""

    sub_elements: list[PatternElement] = field(default_factory=list)
    source_representation: str | None = field(init=False, default=None, compare=False)

    def process(self, file: File, evaluation: EvaluationContext) -> str:
        """Recursively renders pattern as a string"""
        return "".join(
            map(
                lambda se: str(se.process(file, evaluation)),
                self.sub_elements,
            )
        )

    def process_as_expression(self, file: File, evaluation: EvaluationContext) -> str:
        """Recursively renders pattern as an expression string

        In expression string, values returned by the tags are converted using `repr`
        rather than `str` to obtain valid python value representation.
        """
        return "".join(
            map(
                lambda se: PatternElementSequence._convert_to_representation(
                    se, file, evaluation
                ),
                self.sub_elements,
            )
        )

    @staticmethod
    def _convert_to_representation(
        element: PatternElement, file: File, evaluation: EvaluationContext
    ) -> str:
        """Renders value returned by tag invocation as a string representation (as to be used in evaluated
        expressions)"""
        tag_value = element.process(file, evaluation)
        if isinstance(element, TagInstance):
            return repr(tag_value)
        return str(tag_value)


@dataclass
class TagPlaceholder(PatternElement):
    """Represents unbound tag"""

    location: Location = field(init=False, compare=False)
    tag_name: QualifiedTagName
    context: PatternElementSequence | None = None
    args: list[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def process(self, file: File, evaluation: EvaluationContext) -> Any:
        raise NotImplementedError(
            "TagPlaceholder shouldn't be present in bound tag tree"
        )


@dataclass
class TagInstance(PatternElement):
    """Represents a tag bound to the implementation"""

    tag: Tag
    context: PatternElementSequence | None = None
    tag_name: QualifiedTagName | None = field(default=None, compare=False)
    """Name used in the template (for error reporting)"""

    def process(self, file: File, evaluation: EvaluationContext) -> Any:
        context_str = self.context.process(file, evaluation) if self.context else None
        try:
            return self.tag.process(file, context_str)
        except FileMetadataError as error:
            return evaluation.handle_metadata_error(file, self.tag_name, error)
