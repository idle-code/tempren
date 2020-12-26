from pathlib import Path
from typing import Callable, Iterable, Iterator


class File:
    path: Path
    # TODO: add handle for caching open(path) handle - typing.IO?


class Pipeline:
    file_gatherer: Iterator[Path] = None
    filter: Callable[[File], bool] = lambda f: True
    sorter: Callable[[Iterable[File]], Iterable[File]] = None
    name_generator: Callable[[File], Path] = None
    renamer: Callable[[Path, Path], None] = None

    def execute(self):
        # TODO: get file(s)
        # TODO: filter files
        # TODO: sort files
        # TODO: generate new name
        # TODO: rename source file
        pass
