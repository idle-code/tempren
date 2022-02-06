import abc
import re
from abc import ABC
from re import Pattern

from tempren.path_generator import File


class FileFilter:
    @abc.abstractmethod
    def __call__(self, file: File) -> bool:
        raise NotImplementedError


class RegexFileFilter(FileFilter, ABC):
    pattern: Pattern

    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)


class RegexFilenameFileFilter(RegexFileFilter):
    def __call__(self, file: File) -> bool:
        match = self.pattern.fullmatch(file.relative_path.name)
        return match is not None


class RegexPathFileFilter(RegexFileFilter):
    def __call__(self, file: File) -> bool:
        match = self.pattern.fullmatch(str(file.relative_path))
        return match is not None
