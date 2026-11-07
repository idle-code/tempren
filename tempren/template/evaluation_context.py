from typing import Any

from tempren.exceptions import FileMetadataError, MissingMetadataError
from tempren.primitives import File, QualifiedTagName


class SkipFile(Exception):
    """Raised by the evaluation context to exclude currently processed file from the run

    Control flow signal (not an error): catching side drops the file and moves on.
    """


class EvaluationContext:
    """Decides how template rendering reacts when a tag cannot produce a value

    A context is passed explicitly through the whole pattern tree, so a single template
    can be rendered with different policies (e.g. by the CLI and by tests).
    The base implementation propagates the error to the caller.
    """

    def handle_metadata_error(
        self, file: File, tag_name: QualifiedTagName | None, error: FileMetadataError
    ) -> Any:
        """Returns value used in place of the failing tag or raises an exception"""
        raise error


class IgnoreMissingMetadata(EvaluationContext):
    """Renders tags with missing metadata as an empty string"""

    def handle_metadata_error(
        self, file: File, tag_name: QualifiedTagName | None, error: FileMetadataError
    ) -> Any:
        if isinstance(error, MissingMetadataError):
            return ""
        raise error


# Context propagating all tag errors to the caller
propagate_errors = EvaluationContext()
