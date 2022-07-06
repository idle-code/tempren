import logging
import os
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


@dataclass
class RuntimeConfiguration:
    template: str
    input_directory: Path
    dry_run: bool = False
    filter_type: FilterType = FilterType.glob  # TODO: update
    filter_invert: bool = False
    filter: Optional[str] = None
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.stop
    sort_invert: bool = False
    sort: Optional[str] = None
    mode: OperationMode = OperationMode.name


class ConfigurationError(Exception):
    pass


FileRenamerType = Callable[[Path, Path, bool], None]
ManualConflictResolver = Callable[[Path, Path], Union[ConflictResolutionStrategy, Path]]


def manual_resolver_placeholder(
    source_path: Path, destination_path: Path
) -> Union[ConflictResolutionStrategy, Path]:
    raise NotImplementedError()


class Pipeline:
    log: logging.Logger
    _input_directory: Path
    file_gatherer: Callable[[Path], Iterable[Path]]
    sorter: Optional[Callable[[Iterable[File]], Iterable[File]]] = None
    path_generator: PathGenerator
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.stop

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.file_filter: Callable[[File], bool] = lambda file: True
        self.renamer: FileRenamerType = PrintingOnlyRenamer()
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
                self.resolve_conflict(relative_name, new_path, self.conflict_strategy)

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
                "Skipping renaming of %s to %s as destination path already exists",
                source_path,
                destination_path,
            )
        elif strategy == ConflictResolutionStrategy.override:
            self.log.warning(
                "Overriding destination %s as it already exists", destination_path
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
    manual_conflict_resolver: ManualConflictResolver,
) -> Pipeline:
    log.debug("Building pipeline")
    pipeline = Pipeline()
    pipeline.input_directory = config.input_directory
    # TODO: specify base_path
    pipeline.file_gatherer = FileGatherer  # type: ignore
    tree_builder = TagTreeBuilder()

    def _compile_template(template_text: str) -> Pattern:
        log.debug("Compiling template '%s'", template_text)
        try:
            return registry.bind(tree_builder.parse(template_text))
        except TagTemplateError as template_error:
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
        pipeline.renamer = PrintingOnlyRenamer()
    else:
        if config.mode == OperationMode.name:
            pipeline.renamer = FileRenamer()
        elif config.mode == OperationMode.path:
            pipeline.renamer = FileMover()
        else:
            raise NotImplementedError("Unknown operation mode")
    return pipeline
