import logging
from abc import ABC
from pathlib import Path

from tempren.pipeline import File, NameGenerator
from tempren.template.tree_elements import Pattern


class TemplateGenerator(NameGenerator, ABC):
    log: logging.Logger
    pattern: Pattern

    def __init__(self, pattern: Pattern):
        self.log = logging.getLogger(__name__)
        self.log.info("Creating template generator with template: %s", pattern)
        self.pattern = pattern

    def reset(self):
        pass

    def generate_replacement(self, file: File) -> str:
        self.log.debug("Rendering template for %s", file)
        return self.pattern.process(file.path)


class TemplateNameGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:

        return Path(self.generate_replacement(file))


class TemplatePathGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:
        pass
