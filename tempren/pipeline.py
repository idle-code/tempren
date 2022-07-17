import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Optional, Union

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
    DryRunRenamer,
    FileGatherer,
    FileMover,
    FileRenamer,
    FileRenamerType,
    FlatFileGatherer,
    InvalidDestinationError,
    PrintingRenamerWrapper,
    RecursiveFileGatherer,
)
from tempren.path_generator import (
    ExpressionEvaluationError,
    File,
    InvalidFilenameError,
    PathGenerator,
    TemplateEvaluationError,
)
from tempren.template.path_generators import (
    TemplateNameGenerator,
    TemplatePathGenerator,
)
from tempren.template.tree_builder import TagRegistry, TagTreeBuilder, TemplateError
from tempren.template.tree_elements import Pattern

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

    manual = "manual"
    """Prompt user to resolve conflict manually (choose an option or provide new filename)"""


ManualConflictResolver = Callable[[Path, Path], Union[ConflictResolutionStrategy, Path]]


@dataclass
class RuntimeConfiguration:
    template: str
    input_directory: Path
    recursive: bool = False
    include_hidden: bool = False
    dry_run: bool = False
    filter_type: FilterType = FilterType.glob
    filter_invert: bool = False
    filter: Optional[str] = None
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.stop
    sort_invert: bool = False
    sort: Optional[str] = None
    mode: OperationMode = OperationMode.name


class ConfigurationError(Exception):
    pass


def manual_resolver_placeholder(
    source_path: Path, destination_path: Path
) -> Union[ConflictResolutionStrategy, Path]:
    raise NotImplementedError()


class Pipeline:
    log: logging.Logger
    _input_directory: Path
    file_gatherer: FileGatherer
    sorter: Optional[Callable[[Iterable[File]], Iterable[File]]] = None
    path_generator: PathGenerator
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.stop

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.file_filter: Callable[[File], bool] = lambda file: True
        self.renamer: FileRenamerType = DryRunRenamer()
        self.manual_conflict_resolver: ManualConflictResolver = (
            manual_resolver_placeholder
        )

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
        for file in self.file_gatherer.gather_in(self.input_directory):
            self.log.debug("Checking %s", file)
            if not self.file_filter(file):
                self.log.debug("%s filtered out", file)
                continue
            self.log.debug("%s considered for renaming", file)
            all_files.append(file)

        self.log.info("%d files considered for renaming", len(all_files))
        if self.sorter:
            self.log.info("Sorting files")
            all_files = self.sorter(all_files)

        self.log.debug("Generating new names")
        # In case when destination file exists in the first run, we add such name to the
        # backlog and try again (in reverse order) later. This should mitigate most of
        # transitional conflicts.
        backlog = []
        for file in all_files:
            try:
                self.log.debug("Generating new name for %r", file)
                new_relative_path = self.path_generator.generate(file)
                self.log.debug("Generated path: '%s'", new_relative_path)
            except InvalidFilenameError as error:
                # TODO: Introduce flag similar to conflict resolver to take appropriate action
                self.log.warning(
                    "Invalid name generated for %r: %r",
                    file,
                    error.generated_name,
                )
                continue

            # FIXME: check generated new_relative_path for illegal characters (like '*')

            if new_relative_path == file.relative_path:
                # FIXME: Test
                self.log.info(
                    "Skipping renaming of: '%s' (source and destination are the same)",
                    new_relative_path,
                )
                continue

            new_absolute_path = (file.input_directory / new_relative_path).resolve()
            if not str(new_absolute_path).startswith(str(file.input_directory)):
                raise InvalidDestinationError(
                    f"Path generated for {file!r}: {new_relative_path} is not relative to the input directory",
                )

            try:
                self.renamer(file.relative_path, new_relative_path)
            except FileExistsError:
                self.log.debug(
                    "Deferring renaming of %r as destination '%s' already exists",
                    file,
                    new_relative_path,
                )
                backlog.append((file.relative_path, new_relative_path))

        while backlog:
            source_path, destination_path = backlog.pop()
            self.log.debug(
                "Trying again to rename '%s' into '%s'", source_path, destination_path
            )
            try:
                self.renamer(source_path, destination_path)
            except FileExistsError:
                self.resolve_conflict(
                    source_path, destination_path, self.conflict_strategy
                )

    def resolve_conflict(
        self,
        source_path: Path,
        destination_path: Path,
        strategy: ConflictResolutionStrategy,
    ):
        if strategy == ConflictResolutionStrategy.stop:
            raise DestinationAlreadyExistsError(source_path, destination_path)
        elif strategy == ConflictResolutionStrategy.ignore:
            self.log.info(
                "Skipping renaming of '%s' to '%s' as destination path already exists",
                source_path,
                destination_path,
            )
        elif strategy == ConflictResolutionStrategy.override:
            self.log.warning(
                "Overriding destination '%s' as it already exists", destination_path
            )
            self.renamer(source_path, destination_path, True)
        elif strategy == ConflictResolutionStrategy.manual:
            if self.manual_conflict_resolver is None:
                raise NotImplementedError("Manual conflict resolver not configured")
            user_selected_strategy = self.manual_conflict_resolver(
                source_path, destination_path
            )
            if isinstance(user_selected_strategy, Path):
                user_provided_path: Path = user_selected_strategy
                self.renamer(source_path, user_provided_path, False)
            else:
                self.resolve_conflict(
                    source_path, destination_path, user_selected_strategy
                )
        else:
            raise NotImplementedError(
                f"Unknown conflict resolution strategy: {strategy}"
            )


def build_tag_registry() -> TagRegistry:
    log.debug("Building tag registry")
    import tempren.tags

    registry = TagRegistry()
    registry.register_tags_in_package(tempren.tags)
    return registry


def build_pipeline(
    config: RuntimeConfiguration,
    registry: TagRegistry,
    manual_conflict_resolver: ManualConflictResolver,  # TODO: Move to the RuntimeConfiguration
) -> Pipeline:
    log.debug("Building pipeline")
    pipeline = Pipeline()
    pipeline.input_directory = config.input_directory
    tree_builder = TagTreeBuilder()

    if config.recursive:
        pipeline.file_gatherer = RecursiveFileGatherer()
    else:
        pipeline.file_gatherer = FlatFileGatherer()

    pipeline.file_gatherer.include_hidden = config.include_hidden

    def _compile_template(template_text: str) -> Pattern:
        log.debug("Compiling template %r", template_text)
        try:
            return registry.bind(tree_builder.parse(template_text))
        except TemplateError as template_error:
            template_error.template = template_text
            raise template_error

    bound_pattern = _compile_template(config.template)

    if config.mode == OperationMode.name:
        pipeline.path_generator = TemplateNameGenerator(bound_pattern)
        if config.filter:
            if config.filter_type == FilterType.regex:
                pipeline.file_filter = RegexFilenameFileFilter(config.filter)
            elif config.filter_type == FilterType.glob:
                pipeline.file_filter = GlobFilenameFileFilter(config.filter)
            elif config.filter_type == FilterType.template:
                bound_filter_pattern = _compile_template(config.filter)
                pipeline.file_filter = TemplateFileFilter(bound_filter_pattern)
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
                bound_filter_pattern = _compile_template(config.filter)
                pipeline.file_filter = TemplateFileFilter(bound_filter_pattern)
            else:
                raise NotImplementedError("Unknown filter type")
    else:
        raise NotImplementedError("Unknown operation mode")

    if config.filter_invert and config.filter is not None:
        pipeline.file_filter = FileFilterInverter(pipeline.file_filter)

    if config.sort:
        bound_sorter_pattern = _compile_template(config.sort)
        pipeline.sorter = TemplateFileSorter(bound_sorter_pattern, config.sort_invert)

    pipeline.conflict_strategy = config.conflict_strategy
    pipeline.manual_conflict_resolver = manual_conflict_resolver

    if config.dry_run:
        pipeline.renamer = DryRunRenamer()
        # FIXME: Use DryRunMover for path mode?
    else:
        if config.mode == OperationMode.name:
            pipeline.renamer = FileRenamer()
        elif config.mode == OperationMode.path:
            pipeline.renamer = FileMover()
        else:
            raise NotImplementedError("Unknown operation mode")

    pipeline.renamer = PrintingRenamerWrapper(pipeline.renamer)  # type: ignore
    return pipeline
