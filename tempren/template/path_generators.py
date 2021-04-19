import logging
from abc import ABC
from pathlib import Path

from tempren.pipeline import File, PathGenerator
from tempren.template.tree_elements import Pattern


class TemplateGenerator(PathGenerator, ABC):
    log: logging.Logger
    pattern: Pattern

    def __init__(self, start_directory: Path, pattern: Pattern):
        super().__init__(start_directory)
        self.log = logging.getLogger(__name__)
        self.log.info("Creating template generator with template: %s", pattern)
        self.pattern = pattern

    def reset(self):
        pass

    def generate_replacement(self, file: File) -> str:
        relative_path = file.path.relative_to(self.start_directory)
        self.log.debug("Rendering template for '%s'", relative_path)
        return self.pattern.process(relative_path)


class TemplateNameGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:
        return file.path.with_name(self.generate_replacement(file))


class TemplatePathGenerator(TemplateGenerator):
    def generate(self, file: File) -> Path:
        return Path(self.generate_replacement(file))
