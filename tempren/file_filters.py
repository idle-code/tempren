import fnmatch
import logging
import re
from abc import ABC, abstractmethod
from typing import Callable

from tempren.path_generator import (
    ExpressionEvaluationError,
    File,
    TemplateEvaluationError,
    evaluate_expression,
)
from tempren.template.tree_elements import Pattern


class FileFilter(ABC):
    @abstractmethod
    def __call__(self, file: File) -> bool:
        raise NotImplementedError()


class FileFilterInverter(FileFilter):
    def __init__(self, original_filter: Callable[[File], bool]):
        self.original_filter = original_filter

    def __call__(self, file: File) -> bool:
        return not self.original_filter(file)


class RegexFileFilter(FileFilter, ABC):
    pattern: re.Pattern
    ignore_case: bool

    def __init__(self, pattern: str, ignore_case: bool = False):
        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE
        self.pattern = re.compile(pattern, flags)
        self.ignore_case = ignore_case


class RegexFilenameFileFilter(RegexFileFilter):
    def __call__(self, file: File) -> bool:
        match = self.pattern.match(file.relative_path.name)
        return match is not None


class RegexPathFileFilter(RegexFileFilter):
    def __call__(self, file: File) -> bool:
        match = self.pattern.match(str(file.relative_path))
        return match is not None


class GlobFileFilter(FileFilter, ABC):
    pattern: str
    ignore_case: bool

    def __init__(self, pattern: str, ignore_case: bool = False):
        self.pattern = pattern
        self.ignore_case = ignore_case
        if self.ignore_case:
            self.pattern = self.pattern.lower()


class GlobFilenameFileFilter(GlobFileFilter):
    def __call__(self, file: File) -> bool:
        if self.ignore_case:
            return fnmatch.fnmatch(file.relative_path.name.lower(), self.pattern)
        return fnmatch.fnmatchcase(file.relative_path.name, self.pattern)


class GlobPathFileFilter(GlobFileFilter):
    def __call__(self, file: File) -> bool:
        if self.ignore_case:
            return fnmatch.fnmatch(str(file.relative_path).lower(), self.pattern)
        return fnmatch.fnmatchcase(str(file.relative_path), self.pattern)


class TemplateFileFilter(FileFilter):
    log: logging.Logger
    pattern: Pattern

    def __init__(self, pattern: Pattern):
        self.log = logging.getLogger(__name__)
        self.pattern = pattern

    def __call__(self, file: File) -> bool:
        self.log.debug("Rendering filter template for '%s'", file)
        rendered_expression = self.pattern.process_as_expression(file)
        self.log.debug("Evaluating filter expression '%s'", rendered_expression)
        try:
            evaluation_result = evaluate_expression(rendered_expression)
            self.log.debug("Evaluation result '%s'", repr(evaluation_result))
            return bool(evaluation_result)
        except ExpressionEvaluationError as evaluation_error:
            assert self.pattern.source_representation is not None
            raise TemplateEvaluationError(
                file,
                self.pattern.source_representation,
                evaluation_error.expression,
                evaluation_error.message,
            )
