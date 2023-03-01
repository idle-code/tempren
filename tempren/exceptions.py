from tempren.primitives import File


class FileNotSupportedError(Exception):
    """Tag cannot extract value due to invalid file type"""

    pass


class MissingMetadataError(Exception):
    """Tag cannot extract value due to missing metadata"""

    pass


class ExecutionTimeoutError(MissingMetadataError):  # TODO: Fix exception hierarchy?
    """Tag execution time exceeded"""

    pass


class ExpressionEvaluationError(Exception):
    expression: str

    @property
    def message(self) -> str:
        return str(self.__cause__)

    def __init__(self, expression: str):
        self.expression = expression


class TemplateEvaluationError(Exception):
    file: File
    template: str
    expression: str
    message: str

    def __init__(self, file: File, template: str, expression: str, message: str):
        self.file = file
        self.template = template
        self.expression = expression
        self.message = message
