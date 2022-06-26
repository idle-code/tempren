import logging
import os
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Iterable, Optional

from tempren.file_filters import (
    FileFilterInverter,
    GlobFilenameFileFilter,
    GlobPathFileFilter,
    RegexFilenameFileFilter,
    RegexPathFileFilter,
    TemplateFileFilter,
)
from tempren.file_sorters import TemplateFileSorter
from tempren.filesystem import (
    DestinationAlreadyExistsError,
    FileGatherer,
    FileMover,
    FileRenamer,
    PrintingOnlyRenamer,
)
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


# TODO: Find a way to keep documentation close to the enum values and use it in argparser/generated help
class ConflictResolutionStrategy(Enum):
    stop = "stop"
    """Stop renaming and show an error"""

    ignore = "ignore"
    """Leave conflicting record unchanged and continue with renaming"""

    override = "override"
    """Override destination record with a new name"""

    fallback = "fallback"
    """Use fallback template to generate a new name"""

    manual = "manual"
    """Prompt user to resolve conflict manually (choose an option or provide new filename)"""


@dataclass
class RuntimeConfiguration:
    template: str
    input_directory: Path
    dry_run: bool = False
    filter_type: FilterType = FilterType.glob  # TODO: update
    filter_invert: bool = False
    filter: Optional[str] = None
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.stop
    fallback_template: Optional[str] = None
    sort_invert: bool = False
    sort: Optional[str] = None
    mode: OperationMode = OperationMode.name


class ConfigurationError(Exception):
    pass


FileRenamerType = Callable[[Path, Path], None]
ConflictResolver = Callable[[FileRenamerType, Path, Path], None]

conflict_resolver_log = logging.getLogger("ConflictResolver")


def stop_resolver(renamer: FileRenamerType, source_path: Path, destination_path: Path):
    raise DestinationAlreadyExistsError(source_path, destination_path)


def ignore_resolver(
    renamer: FileRenamerType, source_path: Path, destination_path: Path
):
    # conflict_resolver_log.info("Skipping renaming of %s to %s", source_path, source_path)
    print(
        f"Skipping renaming of {source_path} to {destination_path} as destination path already exists"
    )


def override_resolver(
    renamer: FileRenamerType, source_path: Path, destination_path: Path
):
    # TODO: Remove destination file and try again
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
        self.renamer: FileRenamerType = PrintingOnlyRenamer()
        self.conflict_resolver: ConflictResolver = stop_resolver

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
        # In case when destination file exists in the first run, we add such name to the
        # backlog and try again (in reverse order) later. This should mitigate most of
        # transitional conflicts.
        backlog = []
        for file in all_files:
            self.log.debug("Generating new name for %s", file)
            new_path = self.path_generator.generate(file)
            # FIXME: check generated new_path for illegal characters (like '*')
            self.log.debug("Generated path: %s", new_path)
            try:
                self.renamer(file.relative_path, new_path)
            except FileExistsError:
                self.log.debug(
                    "Deferring renaming of %s as destination (%s) already exists",
                    file.relative_path,
                    new_path,
                )
                backlog.append((file.relative_path, new_path))

        while backlog:
            relative_name, new_path = backlog.pop()
            self.log.debug("Trying again to rename %s into %s", relative_name, new_path)
            try:
                self.renamer(relative_name, new_path)
            except FileExistsError:
                self.conflict_resolver(self.renamer, relative_name, new_path)


def build_tag_registry() -> TagRegistry:
    log.info("Building tag registry")
    import tempren.tags

    registry = TagRegistry()
    registry.register_tags_in_package(tempren.tags)
    return registry


def build_pipeline(
    config: RuntimeConfiguration,
    registry: TagRegistry,
    manual_conflict_resolver: ConflictResolver,
) -> Pipeline:
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
                raise NotImplementedError("Unknown filter type")
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
                raise NotImplementedError("Unknown filter type")
    else:
        raise NotImplementedError("Unknown operation mode")

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

    # TODO: Map strategy to actual conflict resolver
    if config.conflict_strategy == ConflictResolutionStrategy.stop:
        pipeline.conflict_resolver = stop_resolver
    elif config.conflict_strategy == ConflictResolutionStrategy.ignore:
        pipeline.conflict_resolver = ignore_resolver
    elif config.conflict_strategy == ConflictResolutionStrategy.override:
        pipeline.conflict_resolver = override_resolver
    elif config.conflict_strategy == ConflictResolutionStrategy.fallback:
        pass  # FIXME: Implement
        # pipeline.conflict_resolver =
    elif config.conflict_strategy == ConflictResolutionStrategy.manual:
        pipeline.conflict_resolver = manual_conflict_resolver

    if config.dry_run:
        pipeline.renamer = PrintingOnlyRenamer()
    else:
        if config.mode == OperationMode.name:
            pipeline.renamer = FileRenamer()
        elif config.mode == OperationMode.path:
            pipeline.renamer = FileMover()
        else:
            raise NotImplementedError("Unknown operation mode")
    return pipeline
