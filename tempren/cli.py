#!/usr/bin/env python
import argparse
import logging
import os.path
import shutil
import sys
from argparse import ArgumentParser, Namespace
from enum import IntEnum
from itertools import chain
from logging import LogRecord
from pathlib import Path
from textwrap import indent
from typing import Any, Dict, List, NoReturn, Optional, Sequence, Text, Tuple, Union

from tempren.exceptions import TemplateEvaluationError
from tempren.filesystem import DestinationAlreadyExistsError
from tempren.primitives import CategoryName, QualifiedTagName, TagName
from tempren.template.exceptions import TagError, TemplateError

from .pipeline import (
    ConflictResolutionStrategy,
    FilterType,
    InvalidDestinationError,
    OperationMode,
    RuntimeConfiguration,
    build_pipeline,
    build_tag_registry,
)

log = logging.getLogger("CLI")


class LogFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__()

    def format(self, record: LogRecord) -> str:
        if logging.root.level <= logging.NOTSET:  # NOCOVER: developer option
            return f"{record.name}:{record.levelname}: {record.getMessage()}"
        if record.levelno == logging.INFO:
            return record.getMessage()
        else:
            return f"{record.levelname}: {record.getMessage()}"


class LogLevelFilter(logging.Filter):
    def __init__(self, min_level: int, max_level: int):
        super().__init__()
        assert min_level <= max_level
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: LogRecord) -> bool:
        return self.min_level <= record.levelno <= self.max_level


# TODO: Use dictConfig for more readability
# CHECK: Move to config module?
def configure_logging():
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.addFilter(LogLevelFilter(0, logging.INFO))
    stdout_handler.setFormatter(LogFormatter())
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.addFilter(LogLevelFilter(logging.WARNING, 1000))
    stderr_handler.setFormatter(LogFormatter())
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(stdout_handler)
    logging.root.addHandler(stderr_handler)


def existing_path(val: str) -> Path:
    input_path = Path(val)
    if not input_path.exists():
        raise argparse.ArgumentTypeError(f"Path '{val}' doesn't exists")
    return input_path


def nonempty_string(val: str) -> str:
    if not val:
        raise argparse.ArgumentTypeError("Non-empty argument required")
    return val


def tag_name_from_executable(exec_path: Path) -> str:
    base_name = os.path.splitext(exec_path.name)[0]
    return base_name


def adhoc_tag(val: str) -> Tuple[TagName, Path]:
    val = nonempty_string(val)
    components = val.split("=", maxsplit=1)
    if len(components) == 1:
        tag_name = None
        exec_path_str = components[0]
    else:
        tag_name, exec_path_str = components
    exec_path = Path(exec_path_str)
    if not exec_path.exists():
        system_exec_path_str = shutil.which(exec_path_str)
        if not system_exec_path_str:
            raise argparse.ArgumentTypeError(f"Executable '{exec_path}' doesn't exists")
        exec_path = Path(system_exec_path_str)
    if not tag_name:
        tag_name = tag_name_from_executable(exec_path)
    try:
        return TagName(tag_name), exec_path.absolute()
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{tag_name}' cannot be used as tag name")


def alias(val: str) -> Tuple[TagName, str]:
    val = nonempty_string(val)
    components = val.split("=", maxsplit=1)
    if len(components) < 2:
        raise argparse.ArgumentTypeError("Missing alias name")

    alias_name, pattern_text = components
    if not pattern_text:
        raise argparse.ArgumentTypeError("Missing alias pattern")

    try:
        return TagName(alias_name), pattern_text
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{alias_name}' cannot be used as tag name")


def validate_adhoc_tags(
    adhoc_tags: List[List[Tuple[TagName, Path]]]
) -> Dict[TagName, Path]:
    if not adhoc_tags:
        return dict()
    list_of_tuples = list(chain(*adhoc_tags))
    names = list(map(lambda pair: pair[0], list_of_tuples))
    unique_names = set(names)
    if len(names) > len(unique_names):
        repeating_names = [name for name in unique_names if names.count(name) > 1]
        for duplicate_name in repeating_names:
            executables_with_the_same_name = list(
                map(
                    lambda pair: str(pair[1]),
                    filter(lambda pair: pair[0] == duplicate_name, list_of_tuples),
                )
            )
            # CHECK: report more errors at once?
            raise SystemExitError(
                ErrorCode.USAGE_ERROR,
                f"Adhoc tags created from executables {' and '.join(executables_with_the_same_name)} cannot have the same name {duplicate_name}",
            )

    return dict(list_of_tuples)


def validate_aliases(aliases: List[List[Tuple[TagName, str]]]) -> Dict[TagName, str]:
    # TODO: Merge with validate_adhoc_tags
    if not aliases:
        return dict()
    list_of_tuples = list(chain(*aliases))
    names = list(map(lambda pair: pair[0], list_of_tuples))
    unique_names = set(names)
    if len(names) > len(unique_names):
        repeating_names = [name for name in unique_names if names.count(name) > 1]
        for duplicate_name in repeating_names:
            patterns_with_the_same_name = list(
                map(
                    lambda pair: str(pair[1]),
                    filter(lambda pair: pair[0] == duplicate_name, list_of_tuples),
                )
            )
            # CHECK: report more errors at once?
            raise SystemExitError(
                ErrorCode.USAGE_ERROR,
                f"Aliases for patterns {' and '.join(patterns_with_the_same_name)} cannot have the same name {duplicate_name}",
            )

    return dict(list_of_tuples)


class SystemExitError(Exception):
    status: int

    def __init__(self, status: int, message: Optional[str]):
        super().__init__(message)
        self.status = status


class _ListAvailableTags(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        args: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        registry = build_tag_registry(
            validate_adhoc_tags(args.ad_hoc), validate_aliases(args.alias)
        )
        log.info("Available tags:")
        for category_name in sorted(registry.category_map.keys()):
            log.info(f"{category_name.capitalize()}:")
            category = registry.category_map[category_name]

            all_category_tags = sorted(category.tag_map.items())
            if not all_category_tags:
                # There is no tags in the category
                # TODO: Empty categories should not be present in the registry
                continue
            max_name_length = max(
                [len(tag_name) for tag_name, factory in all_category_tags]
            )
            log.debug(
                "Longest tag name: %d in category %s", max_name_length, category_name
            )
            for tag_name, factory in all_category_tags:
                log.info(
                    f"  {tag_name.ljust(max_name_length)} - {factory.short_description}"
                )
        parser.exit()


class _ShowHelp(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        args: Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        if values is None:
            parser.print_help()
        else:
            raw_tag_name = str(values)
            registry = build_tag_registry(
                validate_adhoc_tags(args.ad_hoc), validate_aliases(args.alias)
            )

            try:
                if "." in raw_tag_name:
                    category, name = raw_tag_name.split(".")
                    qualified_name = QualifiedTagName(
                        TagName(name), CategoryName(category)
                    )
                else:
                    qualified_name = QualifiedTagName(TagName(raw_tag_name))

                tag_factory = registry.get_tag_factory(qualified_name)
            except TagError as tag_error:
                parser.exit(ErrorCode.USAGE_ERROR, str(tag_error))
                raise
            log.info("")
            log.info(indent(tag_factory.configuration_signature, "  "))
            log.info("")
            log.info(tag_factory.short_description)
            if tag_factory.long_description:
                log.info("")
                log.info(tag_factory.long_description)

        parser.exit()


class _ShowVersion(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        log.info(self.find_package_version())
        parser.exit()

    @staticmethod
    def find_package_version() -> str:  # NOCOVER: hard to test - not worth it
        package_name = "tempren"
        try:
            import importlib.metadata

            return importlib.metadata.version(package_name)
        except ModuleNotFoundError:
            return "0.0.0"


class _IncreaseLogVerbosity(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        root_logger = logging.getLogger()
        root_logger.setLevel(root_logger.level - 10)
        log.debug("Verbosity level set to %d", root_logger.level)


class _DecreaseLogVerbosity(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        root_logger = logging.getLogger()
        root_logger.setLevel(root_logger.level + 10)
        log.debug("Verbosity level set to %d", root_logger.level)


class DefaultOptionsHelpFormatter(argparse.HelpFormatter):
    """Indicates default options in help page"""

    def _get_help_string(self, action):
        if action.default:
            return "(default) " + action.help
        return action.help


# CHECK: use pydantic-cli for argument parsing
def process_cli_configuration(argv: List[str]) -> RuntimeConfiguration:
    log.debug("Parsing command line arguments")
    parser = argparse.ArgumentParser(
        prog="tempren",
        description="Template-based renaming utility",
        fromfile_prefix_chars="@",
        add_help=False,
        formatter_class=DefaultOptionsHelpFormatter,
    )

    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Do not perform any renaming - just show expected operation results",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Look for files in input directory recursively",
    )
    parser.add_argument(
        "-ih",
        "--include-hidden",
        action="store_true",
        help="Consider hidden files and directories when scanning for files in input directory",
    )
    parser.add_argument(
        "-a",
        "--alias",
        nargs=1,
        type=alias,
        action="append",
        metavar="name=pattern",
        help="Add an alias tag rendering given pattern",
    )
    parser.add_argument(
        "-ah",
        "--ad-hoc",
        nargs=1,
        type=adhoc_tag,
        action="append",
        metavar="[name=]program",
        help="Add command or executable as an ad-hoc tag",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action=_IncreaseLogVerbosity,
        nargs=0,
        help="Increase logging verbosity",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action=_DecreaseLogVerbosity,
        nargs=0,
        help="Decrease logging verbosity",
    )

    operation_modes_group = parser.add_argument_group("operation modes")
    operation_mode = operation_modes_group.add_mutually_exclusive_group()
    operation_mode.add_argument(
        "-n",
        "--name",
        action="store_const",
        dest="mode",
        const=OperationMode.name,
        default=OperationMode.name,
        help="Use template to generate file name",
    )
    operation_mode.add_argument(
        "-p",
        "--path",
        action="store_const",
        dest="mode",
        const=OperationMode.path,
        help="Use template to generate relative file path",
    )

    conflict_resolution_group = parser.add_argument_group("conflict resolution")
    conflict_resolution = conflict_resolution_group.add_mutually_exclusive_group()
    conflict_resolution.add_argument(
        "-cs",
        "--conflict-stop",
        action="store_true",
        default=True,
        help="Keep source file name intact and stop",
    )
    conflict_resolution.add_argument(
        "-ci",
        "--conflict-ignore",
        action="store_true",
        help="Keep source file name intact and continue",
    )
    conflict_resolution.add_argument(
        "-co",
        "--conflict-override",
        action="store_true",
        help="Override destination file",
    )
    conflict_resolution.add_argument(
        "-cm",
        "--conflict-manual",
        action="store_true",
        help="Prompt user to resolve conflict manually (choose an option or provide new filename)",
    )

    filtering_group = parser.add_argument_group("filtering")
    filter_mode = filtering_group.add_mutually_exclusive_group()
    filter_mode.add_argument(
        "-fg",
        "--filter-glob",
        type=str,
        metavar="filter_expression",
        help="Globbing filter expression to include individual files",
    )
    filter_mode.add_argument(
        "-fr",
        "--filter-regex",
        type=str,
        metavar="filter_expression",
        help="Regex filter expression to include individual files",
    )
    filter_mode.add_argument(
        "-ft",
        "--filter-template",
        type=nonempty_string,
        metavar="filter_expression",
        help="Tag template filter expression to include individual files",
    )
    filtering_group.add_argument(
        "-fi",
        "--filter-invert",
        action="store_true",
        help="Invert (negate) filter expression result",
    )

    sorting_group = parser.add_argument_group("sorting")
    sorting_group.add_argument(
        "-s",
        "--sort",
        type=nonempty_string,
        metavar="sort_expression",
        help="Sorting tag template used to order file list before processing",
    )
    sorting_group.add_argument(
        "-si",
        "--sort-invert",
        action="store_true",
        help="Reverse sorting order",
    )

    parser.add_argument(
        "template",
        type=nonempty_string,
        help="Template used to generate new filename/path",
    )
    parser.add_argument(
        "path",
        type=existing_path,
        nargs="+",
        help="Input files or directories where files to rename are stored",
    )
    parser.add_argument(
        "-l",
        "--list-tags",
        action=_ListAvailableTags,
        nargs=0,
        help="List available tags and exit",
    )
    parser.add_argument(
        "-h",
        "--help",
        action=_ShowHelp,
        type=str,
        nargs="?",
        metavar="tag_name",
        help="Show help message or tag documentation and exit",
    )
    parser.add_argument(
        "--version",
        action=_ShowVersion,
        nargs=0,
        help="Print version and exit",
    )

    # Upon parsing error, ArgumentParser tries to exit via calling `sys.exit()`.
    # We could catch resulting `SystemExit` exception but related error message still would be missing.
    # This behaviour is not comfortable for testing so here we monkeypatch exit method to
    # throw more practical exception instead.
    def throwing_exit(status: int = 0, message: Optional[str] = "") -> NoReturn:
        raise SystemExitError(status, message)

    parser.exit = throwing_exit  # type: ignore

    args = parser.parse_args(argv)

    if args.filter_glob:
        filter_type = FilterType.glob
        filter_expression = args.filter_glob
    elif args.filter_regex:
        filter_type = FilterType.regex
        filter_expression = args.filter_regex
    elif args.filter_template:
        filter_type = FilterType.template
        filter_expression = args.filter_template
    else:
        filter_type = FilterType.glob
        filter_expression = None

    # TODO: User action='store_const' (as with mode) in parser.add_argument to simplify this
    if args.conflict_ignore:
        conflict_strategy = ConflictResolutionStrategy.ignore
    elif args.conflict_override:
        conflict_strategy = ConflictResolutionStrategy.override
    elif args.conflict_manual:
        conflict_strategy = ConflictResolutionStrategy.manual
    elif args.conflict_stop:
        conflict_strategy = ConflictResolutionStrategy.stop
    else:
        raise NotImplementedError()

    configuration = RuntimeConfiguration(
        template=args.template,
        input_paths=args.path,
        recursive=args.recursive,
        include_hidden=args.include_hidden,
        dry_run=args.dry_run,
        filter_type=filter_type,
        filter_invert=args.filter_invert,
        filter=filter_expression,
        conflict_strategy=conflict_strategy,
        sort_invert=args.sort_invert,
        sort=args.sort,
        mode=args.mode,
        adhoc_tags=validate_adhoc_tags(args.ad_hoc),
        aliases=validate_aliases(args.alias),
    )

    return configuration


def render_template_error(template_error: TemplateError, indent_size: int = 4):
    assert template_error.location.line == 1, "No support for multiline templates yet"
    if template_error.location.length == 1:
        underline = " " * template_error.location.column + "^"
    else:
        underline = (
            " " * template_error.location.column + "~" * template_error.location.length
        )
    log.error("")
    log.error(indent(template_error.template, " " * indent_size))
    log.error(indent(underline, " " * indent_size))
    log.error(f"Template error at {template_error.location}: {template_error.message}")


def render_template_evaluation_error(
    template_error: TemplateEvaluationError, indent_size: int = 4
):
    assert template_error.template
    assert template_error.expression

    log.error("While processing file %r with template:", template_error.file)
    log.error(indent(template_error.template, " " * indent_size))
    log.error("which has been rendered to:")
    log.error(indent(repr(template_error.expression), " " * indent_size))
    log.error("an evaluation error occurred:")
    log.error(indent(template_error.message, " " * indent_size))


def cli_prompt_conflict_resolver(
    source_path: Path, destination_path: Path
) -> Union[ConflictResolutionStrategy, Path]:
    log.warning("White processing:")
    log.warning(f"  {source_path}")
    log.warning("following path was generated:")
    log.warning(f"  {destination_path}")
    log.warning("but it cannot be used as it targets already existing file")
    while True:
        selected_option_name = input(
            "[s]top, [o]verride, [c]ustom path, [I]gnore: "
        ).lower()
        if not selected_option_name or "ignore".startswith(selected_option_name):
            return ConflictResolutionStrategy.ignore
        if "stop".startswith(selected_option_name):
            return ConflictResolutionStrategy.stop
        if "override".startswith(selected_option_name):
            return ConflictResolutionStrategy.override
        if "custom path".startswith(selected_option_name):
            custom_path = Path(input("Custom path: "))
            return custom_path

        log.error(f"Invalid choice '{selected_option_name}")


class ErrorCode(IntEnum):
    SUCCESS = 0
    """Everything went as it should have"""

    INVALID_DESTINATION_ERROR = 1
    """Something is wrong with generated destination path"""

    USAGE_ERROR = 2  # argparse uses 2 for its errors too
    """User tried to use program not as it should be used"""

    TEMPLATE_SYNTAX_ERROR = 3
    """Syntax error detected in one of provided templates"""

    TEMPLATE_EVALUATION_ERROR = 4
    """Python evaluation of filtering/sorting template failed"""

    UNKNOWN_ERROR = 126
    """This should not happen"""


def main() -> int:
    configure_logging()
    argv = sys.argv[1:]
    original_cwd = os.getcwd()
    try:
        config = process_cli_configuration(argv)
        registry = build_tag_registry(config.adhoc_tags, config.aliases)
        pipeline = build_pipeline(
            config, registry, manual_conflict_resolver=cli_prompt_conflict_resolver
        )
        pipeline.execute()
        log.info("Done")
        return ErrorCode.SUCCESS
    # TODO: Clean up exception hierarchy
    except SystemExitError as exc:
        if exc.status != 0:
            log.error(exc)
        return exc.status
    except TemplateEvaluationError as template_evaluation_error:
        render_template_evaluation_error(template_evaluation_error)
        return ErrorCode.TEMPLATE_EVALUATION_ERROR
    except TemplateError as template_error:
        render_template_error(template_error)
        return ErrorCode.TEMPLATE_SYNTAX_ERROR
    except DestinationAlreadyExistsError as exc:
        log.error(f"Error: {exc}")
        return ErrorCode.INVALID_DESTINATION_ERROR
    except InvalidDestinationError as exc:
        log.error(f"Error: {exc}")
        return ErrorCode.INVALID_DESTINATION_ERROR
    except Exception as exc:  # NOCOVER: not really testable - final fallback
        log.error(f"Unknown error: {exc.__class__.__name__} {exc}")
        return ErrorCode.UNKNOWN_ERROR
    finally:
        os.chdir(original_cwd)


def throwing_main():
    sys.exit(main())


if __name__ == "__main__":
    throwing_main()
