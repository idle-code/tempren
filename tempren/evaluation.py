from pathlib import PosixPath
from typing import Any

from tempren.exceptions import ExpressionEvaluationError

_evaluation_locals = {"PosixPath": PosixPath}


def evaluate_expression(python_expression: str) -> Any:
    try:
        evaluation_result = eval(python_expression, {}, _evaluation_locals)
        return evaluation_result
    except Exception as exc:
        raise ExpressionEvaluationError(python_expression) from exc
