import logging
import os
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Optional

from pydantic import BaseModel

from tempren.file_filters import (
    FileFilterInverter,
    GlobFilenameFileFilter,
    GlobPathFileFilter,
    RegexFilenameFileFilter,
    RegexPathFileFilter,
    TemplateFileFilter,
)
from tempren.file_sorters import TemplateFileSorter
from tempren.filesystem import FileGatherer, PrintingOnlyRenamer, Renamer
from tempren.path_generator import File, PathGenerator
from tempren.template.path_generators import (
    TemplateNameGenerator,
    TemplatePathGenerator,
)
from tempren.template.tree_builder import TagRegistry, TagTemplateError, TagTreeBuilder

log = logging.getLogger(__name__)


class FilterType(Enum):
    template = "template"
    regex = "regex"
    glob = "glob"


class OperationMode(Enum):
    name = "name"
    path = "path"


class RuntimeConfiguration(BaseModel):
    dry_run: bool = False
    filter_type: FilterType = FilterType.regex  # TODO: update
    filter_invert: bool = False
    filter: Optional[str] = None
    sort_invert: bool = False
    sort: Optional[str] = None
    mode: OperationMode = OperationMode.name
    template: str
    input_directory: Path


class ConfigurationError(Exception):
    pass


class Pipeline:
    log: logging.Logger
    _input_directory: Path
    file_gatherer: Callable[[Path], Iterable[Path]]
    sorter: Optional[Callable[[Iterable[File]], Iterable[File]]] = None
    path_generator: PathGenerator

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.file_filter: Callable[[File], bool] = lambda file: True
        self.renamer: Callable[[Path, Path], None] = lambda src, dst: None

    @property
    def input_directory(self) -> Path:
        return self._input_directory

    @input_directory.setter
    def input_directory(self, input_path: Path):
        self._input_directory = input_path.absolute()

    def execute(self):
        all_files = []
        self.log.info(f"Gathering paths in {self.input_directory}")
        os.chdir(self.input_directory)
        for path in self.file_gatherer(self.input_directory):
            self.log.debug("Checking %s", path)
            file = File(path.relative_to(self.input_directory))
            if not self.file_filter(file):
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
            self.renamer(file.relative_path, new_path)


def build_tag_registry() -> TagRegistry:
    log.info("Building tag registry")
    import tempren.tags

    registry = TagRegistry()
    registry.register_tags_in_package(tempren.tags)
    return registry


def build_pipeline(config: RuntimeConfiguration, registry: TagRegistry) -> Pipeline:
    log.info("Building pipeline")
    pipeline = Pipeline()
    pipeline.input_directory = config.input_directory
    # TODO: specify base_path
    pipeline.file_gatherer = FileGatherer  # type: ignore
    tree_builder = TagTreeBuilder()

    try:
        bound_pattern = registry.bind(tree_builder.parse(config.template))
    except TagTemplateError as template_error:
        template_error.template = config.template
        raise template_error

    if config.mode == OperationMode.name:
        pipeline.path_generator = TemplateNameGenerator(bound_pattern)
        if config.filter:
            if config.filter_type == FilterType.regex:
                pipeline.file_filter = RegexFilenameFileFilter(config.filter)
            elif config.filter_type == FilterType.glob:
                pipeline.file_filter = GlobFilenameFileFilter(config.filter)
            elif config.filter_type == FilterType.template:
                try:
                    bound_filter_pattern = registry.bind(
                        tree_builder.parse(config.filter)
                    )
                    pipeline.file_filter = TemplateFileFilter(bound_filter_pattern)
                except TagTemplateError as template_error:
                    template_error.template = config.filter
                    raise template_error
            else:
                raise ConfigurationError()
    elif config.mode == OperationMode.path:
        pipeline.path_generator = TemplatePathGenerator(bound_pattern)
        if config.filter:
            if config.filter_type == FilterType.regex:
                pipeline.file_filter = RegexPathFileFilter(config.filter)
            elif config.filter_type == FilterType.glob:
                pipeline.file_filter = GlobPathFileFilter(config.filter)
            elif config.filter_type == FilterType.template:
                try:
                    bound_filter_pattern = registry.bind(
                        tree_builder.parse(config.filter)
                    )
                    pipeline.file_filter = TemplateFileFilter(bound_filter_pattern)
                except TagTemplateError as template_error:
                    template_error.template = config.filter
                    raise template_error
            else:
                raise ConfigurationError()
    else:
        raise ConfigurationError()

    if config.filter_invert and config.filter is not None:
        pipeline.file_filter = FileFilterInverter(pipeline.file_filter)

    if config.sort:
        try:
            bound_sorter_pattern = registry.bind(tree_builder.parse(config.sort))
            pipeline.sorter = TemplateFileSorter(
                bound_sorter_pattern, config.sort_invert
            )
        except TagTemplateError as template_error:
            template_error.template = config.sort
            raise template_error

    if config.dry_run:
        pipeline.renamer = PrintingOnlyRenamer()
    else:
        pipeline.renamer = Renamer()
    return pipeline
