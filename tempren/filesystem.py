from pathlib import Path


class FileGatherer:
    start_directory: Path
    glob_pattern: str  # CHECK: shouldn't globbing be done at the filtering stage?
    # TODO: add an option to include hidden files

    def __init__(self, directory_path: Path, glob_pattern: str = "*"):
        self.start_directory = directory_path
        self.glob_pattern = glob_pattern

    def __iter__(self) -> Path:
        def is_hidden(path: Path) -> bool:
            return path.name.startswith(".")

        yield from filter(
            lambda p: not p.is_dir() and not is_hidden(p),
            self.start_directory.rglob(self.glob_pattern),
        )


class Renamer:
    def __call__(self, source_path: Path, destination_path: Path):
        pass
