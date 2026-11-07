import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable

from tempren.evaluation import evaluate_expression
from tempren.exceptions import ExpressionEvaluationError, TemplateEvaluationError
from tempren.primitives import File, Pattern
from tempren.template.evaluation_context import EvaluationContext, propagate_errors


class FileSorter(ABC):
    @abstractmethod
    def __call__(self, files: Iterable[File]) -> Iterable[File]:
        raise NotImplementedError()


class TemplateFileSorter(FileSorter):
    log: logging.Logger
    pattern: Pattern
    invert: bool = False
    evaluation: EvaluationContext

    def __init__(
        self,
        pattern: Pattern,
        invert: bool = False,
        evaluation: EvaluationContext = propagate_errors,
    ):
        self.log = logging.getLogger(__name__)

        self.pattern = pattern
        self.invert = invert
        self.evaluation = evaluation

    def __call__(self, files: Iterable[File]) -> Iterable[File]:
        return sorted(files, key=self._generate_sort_key, reverse=self.invert)

    def _generate_sort_key(self, file: File) -> tuple:
        self.log.debug("Rendering sorting value template for '%s'", file)
        rendered_expression = (
            "(" + self.pattern.process_as_expression(file, self.evaluation) + ", )"
        )
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


class PathDepthSorter(FileSorter):
    def __call__(self, files: Iterable[File]) -> Iterable[File]:
        return sorted(files, key=lambda f: (len(f.relative_path.parts),), reverse=True)
