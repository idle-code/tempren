import logging
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Iterable, List, Set

from tempren.primitives import File

FileRenamerType = Callable[[Path, Path, bool], None]


class InvalidDestinationError(Exception):
    pass


class DestinationAlreadyExistsError(FileExistsError):
    def __init__(self, src: Path, dst: Path):
        super().__init__(
            f"Could not rename '{src}' as destination path '{dst}' already exists"
        )


class FileGatherer(ABC):
    _include_hidden: bool = (
        False  # CHECK: Make this a parameter to the gather_files method?
    )

    @property
    def include_hidden(self) -> bool:
        """Include hidden files and directories when making the search"""
        return self._include_hidden

    @include_hidden.setter
    def include_hidden(self, include: bool):
        """Include hidden files and directories when making the search"""
        self._include_hidden = include

    @abstractmethod
    def gather_files(self) -> Iterable[File]:
        raise NotImplementedError()


class FilesystemGatherer(FileGatherer, ABC):
    _start_directory: Path
    """Common base directory for gathered files"""

    def _include_path_in_result(self, path: Path) -> bool:
        if not self.include_hidden:
            return not path.name.startswith(".")
        return True


class FlatFileGatherer(FilesystemGatherer):
    def __init__(self, start_directory: Path):
        self._start_directory = start_directory.absolute()

    def gather_files(self) -> Iterable[File]:
        yield from map(
            lambda file_path: File(
                self._start_directory, file_path.relative_to(self._start_directory)
            ),
            filter(
                lambda file_path: self._include_path_in_result(file_path)
                and not file_path.is_dir(),
                self._start_directory.glob("*"),
            ),
        )


class RecursiveFileGatherer(FilesystemGatherer):
    def __init__(self, start_directory: Path):
        self._start_directory = start_directory.absolute()

    def gather_files(self) -> Iterable[File]:
        yield from self._gather_in(self._start_directory)

    def _gather_in(self, directory: Path) -> Iterable[File]:
        for dir_entry in directory.iterdir():
            if not self._include_path_in_result(dir_entry):
                continue

            if dir_entry.is_dir():
                yield from self._gather_in(dir_entry)
            else:
                yield File(
                    self._start_directory, dir_entry.relative_to(self._start_directory)
                )


class ExplicitFileGatherer(FileGatherer):
    def __init__(self, files: List[Path]):
        self._files_to_provide = files

    def gather_files(self) -> Iterable[File]:
        for file in self._files_to_provide:
            yield File(file.parent.absolute(), Path(file.name))


class CombinedFileGatherer(FileGatherer):
    @property
    def include_hidden(self) -> bool:
        raise NotImplementedError()

    @include_hidden.setter
    def include_hidden(self, include: bool):
        for gatherer in self._gatherers:
            gatherer.include_hidden = include

    def __init__(self, gatherers: List[FileGatherer]):
        if not gatherers:
            raise ValueError("No subsequent file gatherers provided")
        self._gatherers = gatherers

    def gather_files(self) -> Iterable[File]:
        for gatherer in self._gatherers:
            yield from gatherer.gather_files()


class FileRenamer:
    def __call__(
        self,
        source_path: Path,
        destination_path: Path,
        override: bool = False,
    ) -> None:
        if not override and destination_path.exists():
            raise DestinationAlreadyExistsError(source_path, destination_path)
        if source_path.parent != destination_path.parent:
            raise InvalidDestinationError(
                f"Destination path {destination_path} targets different directory"
            )
        os.rename(source_path, destination_path)


class FileMover:
    def __call__(
        self,
        source_path: Path,
        destination_path: Path,
        override: bool = False,
    ) -> None:
        if not override and destination_path.exists():
            raise DestinationAlreadyExistsError(source_path, destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), destination_path)


class DryRunRenamer:
    def __init__(self):
        self.removed_paths: Set[Path] = set()
        self.created_paths: Set[Path] = set()

    def __call__(
        self,
        source_path: Path,
        destination_path: Path,
        override: bool = False,
    ) -> None:
        source_exists = (
            source_path.exists() or source_path in self.created_paths
        ) and source_path not in self.removed_paths
        if not source_exists:
            raise FileNotFoundError(f"No such file or directory: {source_path}")

        destination_exists = (
            destination_path.exists() or destination_path in self.created_paths
        ) and destination_path not in self.removed_paths
        if destination_exists and not override:
            raise FileExistsError(
                f"Destination file already exists: {destination_path}"
            )

        self.removed_paths.add(source_path)
        self.created_paths.add(destination_path)
        self.removed_paths.discard(destination_path)
        self.created_paths.discard(source_path)


class PrintingRenamerWrapper:
    log: logging.Logger

    def __init__(self, renamer_to_wrap: FileRenamerType):
        assert renamer_to_wrap is not None
        self.log = logging.getLogger(self.__class__.__name__)
        self.renamer = renamer_to_wrap

    def __call__(
        self,
        source_path: Path,
        destination_path: Path,
        override: bool = False,
    ) -> None:
        if override:
            self.log.debug(
                "Trying to override: %s to %s", source_path, destination_path
            )
        else:
            self.log.debug("Trying to rename: %s to %s", source_path, destination_path)
        self.renamer(source_path, destination_path, override)

        self.log.info(f"Renamed: {source_path}")
        if override:
            self.log.info(f"         to: {destination_path} (override)")
            # self.log.info(f"to existing: {destination_path} (override)")
        else:
            self.log.info(f"     to: {destination_path}")
