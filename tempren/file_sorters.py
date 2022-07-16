import logging
from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from tempren.path_generator import (
    ExpressionEvaluationError,
    File,
    TemplateEvaluationError,
    evaluate_expression,
)
from tempren.template.tree_elements import Pattern


class FileSorter(ABC):
    @abstractmethod
    def __call__(self, files: Iterable[File]) -> Iterable[File]:
        raise NotImplementedError()


class TemplateFileSorter(FileSorter):
    log: logging.Logger
    pattern: Pattern
    invert: bool = False

    def __init__(self, pattern: Pattern, invert: bool = False):
        self.log = logging.getLogger(__name__)

        self.pattern = pattern
        self.invert = invert

    def __call__(self, files: Iterable[File]) -> Iterable[File]:
        return sorted(files, key=self._generate_sort_key, reverse=self.invert)

    def _generate_sort_key(self, file: File) -> Tuple:
        self.log.debug("Rendering sorting value template for '%s'", file)
        rendered_expression = "(" + self.pattern.process_as_expression(file) + ", )"
        self.log.debug("Evaluating sorting value expression '%s'", rendered_expression)
        try:
            evaluation_result = evaluate_expression(rendered_expression)
            self.log.debug("Evaluation result '%s'", repr(evaluation_result))
            return evaluation_result
        except ExpressionEvaluationError as evaluation_error:
            assert self.pattern.source_representation is not None
            raise TemplateEvaluationError(
                file,
                self.pattern.source_representation,
                evaluation_error.expression,
                evaluation_error.message,
            )
