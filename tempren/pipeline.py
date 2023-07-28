import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Union

from tempren.alias import AliasTagFactory, AliasTagFactoryFromClass
from tempren.discovery import discover_aliases_in_package, discover_tags_in_package
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
    CombinedFileGatherer,
    DestinationAlreadyExistsError,
    DryRunRenamer,
    ExplicitFileGatherer,
    FileGatherer,
    FileMover,
    FileRenamer,
    FileRenamerType,
    FlatFileGatherer,
    InvalidDestinationError,
    PrintingRenamerWrapper,
    RecursiveFileGatherer,
)
from tempren.primitives import CategoryName, File, PathGenerator, TagName
from tempren.template.ast import Pattern
from tempren.template.compiler import TemplateCompiler
from tempren.template.exceptions import InvalidFilenameError, TemplateError
from tempren.template.generators import TemplateNameGenerator, TemplatePathGenerator
from tempren.template.parser import TemplateParser
from tempren.template.registry import TagRegistry

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
    input_paths: List[Path]
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
    adhoc_tags: Dict[TagName, Path] = field(default_factory=dict)
    aliases: Dict[TagName, str] = field(default_factory=dict)


class ConfigurationError(Exception):
    pass


def manual_resolver_placeholder(
    source_path: Path, destination_path: Path
) -> Union[ConflictResolutionStrategy, Path]:
    raise NotImplementedError()


class Pipeline:
    log: logging.Logger
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

    def execute(self):
        all_files = []

        self.log.info(f"Gathering paths...")
        for file in self.file_gatherer.gather_files():
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
            # Renamer will receive a relative path,
            # to make it valid we need to change the current directory before processing:
            # TODO: Make renamer operate on File instances instead
            os.chdir(file.input_directory)

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
                raise InvalidDestinationError()
            except Exception as error:
                # TODO: Test
                self.log.error(
                    "Error generated when renaming %r: %r",
                    file,
                    error,
                )
                raise

            if new_relative_path == file.relative_path:
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
            self.log.debug(
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


def build_tag_registry(
    adhoc_tags: Dict[TagName, Path], aliases: Dict[TagName, str]
) -> TagRegistry:
    import tempren.tags

    registry = TagRegistry()
    log.debug("Discovering tags")
    found_tags = discover_tags_in_package(tempren.tags)
    for category_name, tags_in_category in found_tags.items():
        category = registry.register_category(category_name)
        for tag in tags_in_category:
            category.register_tag_class(tag)

    if adhoc_tags:
        log.debug("Registering ad-hoc tags")
        adhoc_category = registry.register_category(CategoryName("AdHoc"))
        for tag_name, exec_path in sorted(adhoc_tags.items()):
            adhoc_category.register_tag_from_executable(exec_path, tag_name)

    log.debug("Discovering tag aliases")
    found_aliases = discover_aliases_in_package(tempren.tags)
    compiler = TemplateCompiler(registry)
    for category_name, aliases_in_category in found_aliases.items():
        alias_category = registry.find_category(category_name)
        if not alias_category:
            alias_category = registry.register_category(category_name)

        for alias in aliases_in_category:
            alias_tag_factory = AliasTagFactoryFromClass(alias, compiler)
            alias_category.register_tag_factory(alias_tag_factory)

    if aliases:
        log.debug("Registering ad-hoc aliases")
        alias_category = registry.register_category(CategoryName("Alias"))
        for alias_name, pattern_text in sorted(aliases.items()):
            alias_category.register_tag_factory(
                AliasTagFactory(alias_name, pattern_text, compiler)
            )

    return registry


def build_pipeline(
    config: RuntimeConfiguration,
    registry: TagRegistry,
    manual_conflict_resolver: ManualConflictResolver,  # TODO: Move to the RuntimeConfiguration
) -> Pipeline:
    log.debug("Building pipeline")
    pipeline = Pipeline()

    file_gatherers: List[FileGatherer] = []
    input_directories = filter(lambda p: p.is_dir(), config.input_paths)
    for directory in input_directories:
        if config.recursive:
            file_gatherers.append(RecursiveFileGatherer(directory))
        else:
            file_gatherers.append(FlatFileGatherer(directory))

    input_files = list(filter(lambda p: p.is_file(), config.input_paths))
    if any(input_files):
        file_gatherers.append(ExplicitFileGatherer(input_files))
    pipeline.file_gatherer = CombinedFileGatherer(file_gatherers)
    pipeline.file_gatherer.include_hidden = config.include_hidden

    compiler = TemplateCompiler(registry)

    def _compile_template(template_text: str) -> Pattern:
        try:
            return compiler.compile(template_text)
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
