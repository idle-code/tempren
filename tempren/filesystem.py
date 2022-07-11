import logging
import os
import shutil
from pathlib import Path
from typing import Callable, Generator, Set

FileRenamerType = Callable[[Path, Path, bool], None]


class InvalidDestinationError(Exception):
    pass


class DestinationAlreadyExistsError(FileExistsError):
    def __init__(self, src: Path, dst: Path):
        super().__init__(
            f"Could not rename '{src}' as destination path '{dst}' already exists"
        )


class FileGatherer:
    start_directory: Path
    glob_pattern: str  # TODO: globbing should be done at the filtering stage
    # TODO: add an option to include hidden files

    def __init__(self, directory_path: Path, glob_pattern: str = "*"):
        self.start_directory = directory_path
        self.glob_pattern = glob_pattern

    def __iter__(self) -> Generator[Path, None, None]:
        def is_hidden(path: Path) -> bool:
            return path.name.startswith(".")

        # os.chdir(self.start_directory)  # FIXME: implement

        yield from filter(
            lambda p: not p.is_dir() and not is_hidden(p),
            self.start_directory.rglob(self.glob_pattern),
        )


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

        self.log.info(f"\nRenamed: {source_path}")
        if override:
            self.log.info(f"     to: {destination_path} (override)")
        else:
            self.log.info(f"     to: {destination_path}")
