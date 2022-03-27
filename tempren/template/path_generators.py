import logging
from abc import ABC
from pathlib import Path

from tempren.path_generator import File, PathGenerator
from tempren.template.tree_elements import Pattern


class TemplateGenerator(PathGenerator, ABC):
    log: logging.Logger
    pattern: Pattern

    def __init__(self, pattern: Pattern):
        self.log = logging.getLogger(__name__)
        self.log.debug("Creating template generator with template: %s", pattern)
        self.pattern = pattern

    def reset(self):
        pass

    def generate_replacement(self, file: File) -> str:
        self.log.debug("Rendering template for '%s'", file.relative_path)
        return self.pattern.process(file.relative_path)


class TemplateNameGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:
        return file.relative_path.with_name(self.generate_replacement(file))


class TemplatePathGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:
        return Path(self.generate_replacement(file))
