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
└── DestinationError              - generated destination path cannot be used
    ├── InvalidDestinationError
    ├── InvalidFilenameError      (see tempren.template.exceptions)
    └── DestinationAlreadyExistsError
"""

from pathlib import Path

from tempren.primitives import File


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


class DestinationError(TemprenError):
    """Generated destination path cannot be used"""


class InvalidDestinationError(DestinationError):
    pass


class DestinationAlreadyExistsError(DestinationError, FileExistsError):
    def __init__(self, src: Path, dst: Path):
        super().__init__(
            f"Could not rename '{src}' as destination path '{dst}' already exists"
        )
