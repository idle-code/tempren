import re
from abc import ABC, abstractmethod
from re import Pattern

from tempren.path_generator import File


class FileFilter(ABC):
    @abstractmethod
    def __call__(self, file: File) -> bool:
        raise NotImplementedError()


class RegexFileFilter(FileFilter, ABC):
    pattern: Pattern
    invert: bool
    ignore_case: bool

    def __init__(self, pattern: str, invert: bool = False, ignore_case: bool = False):
        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE
        self.pattern = re.compile(pattern, flags)
        self.invert = invert
        self.ignore_case = ignore_case


class RegexFilenameFileFilter(RegexFileFilter):
    def __call__(self, file: File) -> bool:
        match = self.pattern.match(file.relative_path.name)
        return (match is not None) != self.invert


class RegexPathFileFilter(RegexFileFilter):
    def __call__(self, file: File) -> bool:
        match = self.pattern.match(str(file.relative_path))
        return (match is not None) != self.invert
