import logging

from tempren.template.ast import Pattern
from tempren.template.exceptions import TemplateError
from tempren.template.parser import TemplateParser
from tempren.template.registry import TagRegistry


class TemplateCompiler:
    log: logging.Logger
    parser = TemplateParser()
    registry: TagRegistry

    def __init__(self, registry: TagRegistry):
        self.log = logging.getLogger(__name__)
        self.parser = TemplateParser()
        self.registry = registry

    def compile(self, template_text: str) -> Pattern:
        self.log.debug("Compiling template %r", template_text)
        try:
            return self.registry.bind(self.parser.parse(template_text))
        except TemplateError as template_error:
            template_error.template = template_text
            raise
