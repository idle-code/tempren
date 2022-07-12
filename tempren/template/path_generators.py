import logging
from abc import ABC
from pathlib import Path

from tempren.path_generator import File, InvalidFilenameError, PathGenerator
from tempren.template.tree_elements import Pattern


class TemplateGenerator(PathGenerator, ABC):
    log: logging.Logger
    pattern: Pattern

    def __init__(self, pattern: Pattern):
        self.log = logging.getLogger(__name__)
        self.log.debug("Creating template generator with template: %s", pattern)
        self.pattern = pattern

    def generate_replacement(self, file: File) -> str:
        self.log.debug("Rendering template for '%s'", file.relative_path)
        rendered_template = self.pattern.process(file)
        self.log.debug("Rendered template: '%s'", rendered_template)
        return rendered_template


class TemplateNameGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:
        new_name = self.generate_replacement(file)
        try:
            return file.relative_path.with_name(new_name)
        except ValueError:
            raise InvalidFilenameError(new_name)


class TemplatePathGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:
        return Path(self.generate_replacement(file))
