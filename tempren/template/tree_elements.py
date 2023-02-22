import subprocess
import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple, Type

from docstring_parser import parse as parse_docstring

from tempren.path_generator import File


@dataclass
class TagName:
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
    """Represents element of template pattern"""

    @abstractmethod
    def process(self, file: File) -> Any:
        raise NotImplementedError()


@dataclass
class RawText(PatternElement):
    """Represents constant text (non-tag) part of the template"""

    location: Location = field(init=False, compare=False)
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
    tag_name: TagName
    context: Optional[Pattern] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def process(self, file: File) -> str:
        raise NotImplementedError(
            "TagPlaceholder shouldn't be present in bound tag tree"
        )


class FileNotSupportedError(Exception):
    """Tag cannot extract value due to invalid file type"""

    pass


class MissingMetadataError(Exception):
    """Tag cannot extract value due to missing metadata"""

    pass


class ExecutionTimeoutError(MissingMetadataError):  # TODO: Fix hierarchy?
    """Tag execution time exceeded"""

    pass


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
        signature_start_length = 1 + len(self.tag_name) + 1
        return "\n".join(
            (
                single_line_signature,
                textwrap.indent(argument_description, " " * signature_start_length),
            )
        )

    def _create_configuration_signature(self) -> str:
        import inspect

        signature = inspect.signature(self._tag_class.configure)
        parameters_without_self = list(
            filter(lambda param: param.name != "self", signature.parameters.values())
        )
        signature_str = str(signature.replace(parameters=parameters_without_self))
        if self._tag_class.require_context is None:
            context_metavar = "[{...}]"
        elif self._tag_class.require_context is True:
            context_metavar = "{...}"  # TODO: test?
            if not parameters_without_self:
                # Empty argument list can be skipped for context-only tags
                signature_str = ""
        else:
            context_metavar = ""
        single_line_signature = f"%{self._tag_name}{signature_str}{context_metavar}"
        return single_line_signature

    def _create_arguments_description(self) -> Optional[str]:
        argument_description = []
        for argument in self._parsed_configure_docstring.params:
            argument_description.append(f"{argument.arg_name} - {argument.description}")
        if not argument_description:
            return None
        return "\n".join(argument_description)

    @property
    def short_description(self) -> str:
        if self._parsed_class_docstring.short_description:
            return self._parsed_class_docstring.short_description
        return ""

    @property
    def long_description(self) -> Optional[str]:
        return self._parsed_class_docstring.long_description

    def __init__(self, tag_class: Type[Tag], tag_name: str):
        self._tag_class = tag_class
        self._tag_name = tag_name
        self._parsed_class_docstring = parse_docstring(
            tag_class.__doc__ if tag_class.__doc__ else ""
        )
        self._parsed_configure_docstring = parse_docstring(
            tag_class.configure.__doc__ if tag_class.configure.__doc__ else ""
        )

    def __call__(self, *args, **kwargs) -> Tag:
        tag = self._tag_class()
        tag.configure(*args, **kwargs)  # type: ignore
        return tag


class TagFactoryFromExecutable(TagFactoryFromClass):
    _executable_path: Path

    def __init__(self, exec_path: Path, tag_name: str):
        assert exec_path.exists()
        self._executable_path = exec_path
        super().__init__(AdHocTag, tag_name)

    def __call__(self, *args, **kwargs) -> Tag:
        tag = AdHocTag(self._executable_path)
        tag.configure(*args, **kwargs)  # type: ignore
        return tag


class AdHocTag(Tag):
    executable: Path
    args: Tuple[str, ...] = ()
    timeout_ms: int = 3000

    def __init__(self, executable: Path):
        assert (
            executable.exists()
        ), "Provided executable doesn't exists in the filesystem"
        self.executable = executable

    def configure(self, *positional_args: str, timeout_ms: int = 3000):
        """
        :param positional_args: arguments to be passed to the executable
        :param timeout_ms: execution timeout in milliseconds
        """
        self.args = positional_args
        self.timeout_ms = timeout_ms

    def process(self, file: File, context: Optional[str]) -> str:
        if context is None:
            command_line = (
                [str(self.executable)] + list(self.args) + [str(file.relative_path)]
            )
        else:
            command_line = [str(self.executable)] + list(self.args)

        try:
            completed_process = subprocess.run(
                command_line,
                input=context.encode("utf-8") if context else None,
                capture_output=True,
                timeout=self.timeout_ms / 1000,
                cwd=file.input_directory,
            )
        except subprocess.TimeoutExpired:
            raise ExecutionTimeoutError(
                "`{}` command execution exceeded timeout {}ms".format(
                    " ".join(command_line), self.timeout_ms
                )
            )

        captured_stdout = completed_process.stdout.decode("utf-8")
        if completed_process.returncode != 0:
            captured_stderr = completed_process.stderr.decode("utf-8")
            raise MissingMetadataError(
                "Command failed due to error code ({}): \n{}".format(
                    completed_process.returncode, captured_stderr
                )
            )
        return captured_stdout.strip()


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
