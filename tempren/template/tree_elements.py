import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, List, Mapping, Optional, Type

from docstring_parser import parse as parse_docstring


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
        """Renders value returned by tag invocation as a string"""
        if isinstance(tag_value, str):
            return tag_value
        return repr(tag_value)

    def process_as_expression(self, path: Path) -> str:
        return "".join(
            map(
                lambda se: Pattern._convert_to_representation(se, path),
                self.sub_elements,
            )
        )

    @staticmethod
    def _convert_to_representation(element: PatternElement, path: Path) -> str:
        """Renders value returned by tag invocation as a string representation (as to be used in evaluated
        expressions)"""
        tag_value = element.process(path)
        if isinstance(element, TagInstance):
            return repr(tag_value)
        return Pattern._convert_tag_value(tag_value)


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
            "TagPlaceholder shouldn't be present in bound tag tree"
        )


class Tag(ABC):
    require_context: Optional[bool] = None

    def configure(self):
        pass

    @abstractmethod
    def process(self, path: Path, context: Optional[str]) -> Any:
        raise NotImplementedError()


class TagFactory(ABC):
    @property
    @abstractmethod
    def tag_name(self) -> str:
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


class TagFactoryFromClass(TagFactory):
    _tag_class_suffix = "Tag"
    _tag_class: Type[Tag]
    _tag_name: str

    @property
    def tag_name(self) -> str:
        return self._tag_name

    @property
    def configuration_signature(self) -> str:
        single_line_signature = self._create_configuration_signature()
        argument_description = self._create_arguments_description()
        if argument_description is None:
            return single_line_signature
        return "\n".join((single_line_signature, argument_description))

    def _create_configuration_signature(self) -> str:
        import inspect

        signature = inspect.signature(self._tag_class.configure)
        parameters_without_self = list(
            filter(lambda param: param.name != "self", signature.parameters.values())
        )
        signature = signature.replace(parameters=parameters_without_self)
        if self._tag_class.require_context is None:
            context_metavar = "[{...}]"
        elif self._tag_class.require_context is True:
            context_metavar = "{...}"
        else:
            context_metavar = ""
        single_line_signature = f"%{self._tag_name}{signature}{context_metavar}"
        return single_line_signature

    def _create_arguments_description(self) -> Optional[str]:
        argument_description = []
        for argument in self._parsed_configure_docstring.params:
            argument_description.append(f"{argument.arg_name} - {argument.description}")
        if not argument_description:
            return None
        return textwrap.indent("\n".join(argument_description), "  ")

    @property
    def short_description(self) -> str:
        if self._parsed_class_docstring.short_description:
            return self._parsed_class_docstring.short_description
        return ""

    @property
    def long_description(self) -> Optional[str]:
        return self._parsed_class_docstring.long_description

    def __init__(self, tag_class: Type[Tag], tag_name: Optional[str] = None):
        self._tag_class = tag_class
        self._parsed_class_docstring = parse_docstring(
            tag_class.__doc__ if tag_class.__doc__ else ""
        )
        self._parsed_configure_docstring = parse_docstring(
            tag_class.configure.__doc__ if tag_class.configure.__doc__ else ""
        )
        if tag_name:
            self._tag_name = tag_name
        else:
            tag_class_name = tag_class.__name__
            if tag_class_name.endswith(self._tag_class_suffix):
                self._tag_name = tag_class_name[: -len(self._tag_class_suffix)]
            else:
                raise ValueError(
                    f"Could not determine tag name from tag class: {tag_class_name}"
                )

    def __call__(self, *args, **kwargs) -> Tag:
        tag = self._tag_class()
        tag.configure(*args, **kwargs)  # type: ignore
        return tag


@dataclass
class TagInstance(PatternElement):
    tag: Tag
    context: Optional[Pattern] = None

    def process(self, path: Path) -> Any:
        context_str = self.context.process(path) if self.context else None
        return self.tag.process(path, context_str)
