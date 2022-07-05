import logging
import os
import shutil
from pathlib import Path
from typing import Generator, Optional


class InvalidDestinationError(Exception):
    pass


class DestinationAlreadyExistsError(FileExistsError):
    def __init__(self, src: Path, dst: Path):
        super().__init__(
            f"Could not rename {src} as destination path {dst} already exists"
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
        if source_path == destination_path:
            return
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
        if source_path == destination_path:
            return
        if not override and destination_path.exists():
            raise DestinationAlreadyExistsError(source_path, destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), destination_path)


class PrintingOnlyRenamer:
    log: logging.Logger

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def __call__(
        self,
        source_path: Path,
        destination_path: Path,
        override: bool = False,
    ) -> None:
        if source_path == destination_path:
            self.log.info("Skipping renaming: source and destination are the same")
            return
        if destination_path.exists() and not override:
            self.log.info("Skipping renaming: destination path exists")
            raise FileExistsError(
                f"Destination file already exists: {destination_path}"
            )
        if not source_path.exists():
            raise FileNotFoundError(f"No such file or directory: {source_path}")

        self.log.info(f"\nRenaming: {source_path}")
        if override:
            self.log.info(f"      to: {destination_path} (override)")
        else:
            self.log.info(f"      to: {destination_path}")
