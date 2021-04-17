import logging
import os
from pathlib import Path
from typing import Generator


class FileGatherer:
    start_directory: Path
    glob_pattern: str  # CHECK: shouldn't globbing be done at the filtering stage?
    # TODO: add an option to include hidden files

    def __init__(self, directory_path: Path, glob_pattern: str = "*"):
        self.start_directory = directory_path
        self.glob_pattern = glob_pattern

    def __iter__(self) -> Generator[Path, None, None]:
        def is_hidden(path: Path) -> bool:
            return path.name.startswith(".")

        yield from filter(
            lambda p: not p.is_dir() and not is_hidden(p),
            self.start_directory.rglob(self.glob_pattern),
        )


class Renamer:
    def __call__(self, source_path: Path, destination_path: Path):
        if source_path == destination_path:
            return
        if destination_path.exists():
            raise FileExistsError(
                f"Destination file already exists: {destination_path}"
            )
        os.rename(source_path, destination_path)


class PrintingOnlyRenamer:
    log: logging.Logger

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def __call__(self, source_path: Path, destination_path: Path):
        if source_path == destination_path:
            self.log.debug("Skipping renaming: source and destination are the same")
            return
        if destination_path.exists():
            self.log.debug("Skipping renaming: destination path exists")
            raise FileExistsError(
                f"Destination file already exists: {destination_path}"
            )
        self.log.info("Renaming '%s' -> '%s'", source_path, destination_path)
