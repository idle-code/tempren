import logging
from pathlib import Path
from typing import Callable, Iterable, Iterator, Optional

from pydantic import BaseModel

from tempren.filesystem import FileGatherer, PrintingOnlyRenamer, Renamer
from tempren.path_generator import File, PathGenerator
from tempren.template.path_generators import (
    TemplateNameGenerator,
    TemplatePathGenerator,
)
from tempren.template.tree_builder import TagRegistry, TagTreeBuilder

log = logging.getLogger(__name__)


class RuntimeConfiguration(BaseModel):
    input_directory: Path
    name: bool = False
    path: bool = False
    template: str
    dry_run: bool = False


class ConfigurationError(Exception):
    pass


class Pipeline:
    log: logging.Logger
    file_gatherer: Iterator[Path]
    sorter: Optional[Callable[[Iterable[File]], Iterable[File]]] = None
    path_generator: PathGenerator

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.filter: Callable[[File], bool] = lambda f: True
        self.renamer: Callable[[Path, Path], None] = lambda src, dst: None

    def execute(self):
        all_files = []
        self.log.info("Gathering paths")
        for path in self.file_gatherer:
            self.log.debug("Checking %s", path)
            file = File(path)
            if not self.filter(file):
                self.log.debug("%s filtered out", file)
                continue
            self.log.debug("%s considered for renaming", file)
            all_files.append(file)

        self.log.info("%d files considered for renaming", len(all_files))
        self.log.info("Sorting files")
        if self.sorter:
            all_files = self.sorter(all_files)

        self.log.info("Generating new names")
        for file in all_files:
            self.log.debug("Generating new name for %s", file)
            new_path = self.path_generator.generate(file)
            # FIXME: check generated new_path for illegal characters (like '*')
            self.log.debug("Generated path: %s", new_path)
            self.renamer(file.path, new_path)


def build_tag_registry() -> TagRegistry:
    log.info("Building tag registry")
    import tempren.plugins.tags

    registry = TagRegistry()
    registry.register_tags_in_package(tempren.plugins.tags)
    return registry


def build_pipeline(config: RuntimeConfiguration, registry: TagRegistry) -> Pipeline:
    log.info("Building pipeline")
    pipeline = Pipeline()
    # TODO: specify base_path
    config.input_directory = config.input_directory
    pipeline.file_gatherer = iter(FileGatherer(config.input_directory))
    tree_builder = TagTreeBuilder()

    if config.name:
        bound_pattern = registry.bind(tree_builder.parse(config.template))
        pipeline.path_generator = TemplateNameGenerator(
            config.input_directory, bound_pattern
        )
    elif config.path:
        bound_pattern = registry.bind(tree_builder.parse(config.template))
        pipeline.path_generator = TemplatePathGenerator(
            config.input_directory, bound_pattern
        )
    else:
        raise ConfigurationError()

    if config.dry_run:
        pipeline.renamer = PrintingOnlyRenamer()
    else:
        pipeline.renamer = Renamer()
    return pipeline
