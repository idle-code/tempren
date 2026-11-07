"""Exception hierarchy shared by all tempren components

TemprenError
├── ConfigurationError            - invalid runtime configuration
├── TemplateError                 - error in the template itself (see tempren.template.exceptions)
├── ExpressionEvaluationError     - Python expression evaluation failed
├── TemplateEvaluationError       - filtering/sorting template evaluation failed for a file
├── FileMetadataError             - tag cannot extract value from the processed file
│   ├── FileNotSupportedError
│   └── MissingMetadataError
│       └── ExecutionTimeoutError
├── MetadataUnavailableError      - tag in the template had no value for a file
└── DestinationError              - generated destination path cannot be used
    ├── InvalidDestinationError
    ├── InvalidFilenameError      (see tempren.template.exceptions)
    └── DestinationAlreadyExistsError
"""

from pathlib import Path

from tempren.primitives import File, QualifiedTagName


class TemprenError(Exception):
    """Base class for all errors reported by tempren

    String representation of the exception should be a message readable by the user.
    """


class ConfigurationError(TemprenError):
    """Runtime configuration is not valid"""


class ExpressionEvaluationError(TemprenError):
    expression: str

    @property
    def message(self) -> str:
        return str(self.__cause__)

    def __init__(self, expression: str):
        super().__init__(f"Evaluation of expression failed: {expression}")
        self.expression = expression


class TemplateEvaluationError(TemprenError):
    file: File
    template: str
    expression: str
    message: str

    def __init__(self, file: File, template: str, expression: str, message: str):
        super().__init__(message)
        self.file = file
        self.template = template
        self.expression = expression
        self.message = message


class FileMetadataError(TemprenError):
    """Tag cannot extract value from the processed file"""


class FileNotSupportedError(FileMetadataError):
    """Tag cannot extract value due to invalid file type"""

    def __init__(self):
        super().__init__(self.__doc__)


class MissingMetadataError(FileMetadataError):
    """Tag cannot extract value due to missing metadata"""


class ExecutionTimeoutError(MissingMetadataError):
    """Tag execution time exceeded"""


class MetadataUnavailableError(TemprenError):
    """Tag used in the template could not produce a value for the processed file

    Wraps FileMetadataError raised by the tag (available as `__cause__`) with
    the information where it happened.
    """

    file: File
    tag_name: QualifiedTagName | None
    reason: str

    def __init__(
        self, file: File, tag_name: QualifiedTagName | None, reason: FileMetadataError
    ):
        self.file = file
        self.tag_name = tag_name
        self.reason = str(reason)
        tag = f"%{tag_name}()" if tag_name else "tag"
        super().__init__(f"{tag} has no value for '{file}': {self.reason}")


class DestinationError(TemprenError):
    """Generated destination path cannot be used"""


class InvalidDestinationError(DestinationError):
    pass


class DestinationAlreadyExistsError(DestinationError, FileExistsError):
    def __init__(self, src: Path, dst: Path):
        super().__init__(
            f"Could not rename '{src}' as destination path '{dst}' already exists"
        )
