import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Iterable, Iterator, Optional


class File:
    path: Path
    # TODO: add handle for caching open(path) handle - typing.IO?

    def __init__(self, path: Path):
        self.path = path

    def __str__(self):
        return f"File({repr(str(self.path))})"


class NameGenerator(ABC):
    @abstractmethod
    def reset(self):
        raise NotImplementedError()

    @abstractmethod
    def generate(self, file: File) -> Path:
        raise NotImplementedError()


class Pipeline:
    log: logging.Logger
    file_gatherer: Iterator[Path] = None
    filter: Callable[[File], bool]
    sorter: Optional[Callable[[Iterable[File]], Iterable[File]]] = None
    name_generator: NameGenerator = None
    renamer: Callable[[Path, Path], None] = None

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.filter = lambda f: True

    def execute(self):
        all_files = []
        self.log.info("Gathering paths")
        for path in self.file_gatherer:
            self.log.debug("Checking %s", path)
            file = File(path)
            if not self.filter(file):
                self.log.debug("%s filtered out", file)
                continue
            self.log.debug("%s considered for renaming", file)
            all_files.append(file)

        self.log.info("%d files considered for renaming", len(all_files))
        self.log.info("Sorting files")
        if self.sorter:
            all_files = self.sorter(all_files)

        self.log.info("Generating new names")
        for file in all_files:
            self.log.debug("Generating new name for %s", file)
            new_path = self.name_generator.generate(file)
            self.log.debug("Generated name: %s", new_path)
            self.renamer(file.path, new_path)
