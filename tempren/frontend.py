"""Interface between the renaming pipeline and its user-facing frontend (CLI, GUI, ...)"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from tempren.exceptions import MetadataUnavailableError
from tempren.primitives import File

if TYPE_CHECKING:  # NOCOVER: import cycle - pipeline module depends on this one
    from tempren.pipeline import ConflictResolutionStrategy, MissingMetadataStrategy


class SkipReason(Enum):
    same_path = "same_path"
    """Generated path is the same as the source one"""

    conflict_ignored = "conflict_ignored"
    """Destination path already exists and the conflict was ignored"""

    missing_metadata = "missing_metadata"
    """Tag used in one of the templates could not produce a value for the file"""


class Frontend(Protocol):
    """Receives pipeline progress/results and resolves situations requiring user decision

    Paths passed to the frontend are relative to the file's input directory.
    """

    def resolve_conflict(
        self, source: File, destination: Path
    ) -> ConflictResolutionStrategy | Path:
        """Select how to resolve conflict when destination path already exists

        Returned path is treated as a custom destination (relative to the input directory).
        """
        ...

    def resolve_missing_metadata(
        self, error: MetadataUnavailableError
    ) -> MissingMetadataStrategy | str:
        """Select how to proceed when a tag cannot produce a value for a file

        Returned string is used as the tag value.
        """
        ...

    def files_gathered(self, count: int) -> None:
        """Notifies how many files (after filtering) will be processed"""
        ...

    def file_renamed(self, source: File, destination: Path, overridden: bool) -> None:
        """Notifies that the file was renamed (or would be, in dry-run mode)"""
        ...

    def file_skipped(
        self,
        source: File,
        destination: Path | None,
        reason: SkipReason,
        error: MetadataUnavailableError | None = None,
    ) -> None:
        """Notifies that the file was left intact

        Destination is not known when the file was skipped before its new name was
        generated (missing metadata) - `error` describes the cause then.
        """
        ...


class NullFrontend:
    """Frontend ignoring all notifications; manual resolution is not supported"""

    def resolve_conflict(
        self, source: File, destination: Path
    ) -> ConflictResolutionStrategy | Path:
        raise NotImplementedError("Manual conflict resolution is not supported")

    def resolve_missing_metadata(
        self, error: MetadataUnavailableError
    ) -> MissingMetadataStrategy | str:
        raise NotImplementedError("Manual missing metadata resolution is not supported")

    def files_gathered(self, count: int) -> None:
        pass

    def file_renamed(self, source: File, destination: Path, overridden: bool) -> None:
        pass

    def file_skipped(
        self,
        source: File,
        destination: Path | None,
        reason: SkipReason,
        error: MetadataUnavailableError | None = None,
    ) -> None:
        pass
