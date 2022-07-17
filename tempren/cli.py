#!/usr/bin/env python
import argparse
import logging
import sys
from argparse import ArgumentParser, Namespace
from logging import LogRecord
from pathlib import Path
from textwrap import indent
from typing import Any, List, NoReturn, Optional, Sequence, Text, Union

from .pipeline import (
    ConflictResolutionStrategy,
    FilterType,
    InvalidDestinationError,
    OperationMode,
    RuntimeConfiguration,
    TemplateEvaluationError,
    build_pipeline,
    build_tag_registry,
)
from .template.tree_builder import TemplateError

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


def existing_directory(val: str) -> Path:
    directory_path = Path(val)
    if not directory_path.is_dir():
        raise argparse.ArgumentTypeError(f"Directory '{val}' doesn't exists")
    return directory_path


def nonempty_string(val: str) -> str:
    if not val:
        raise argparse.ArgumentTypeError(f"Non-empty argument required")
    return val


class SystemExitError(Exception):
    status: int

    def __init__(self, status: int, message: Optional[str]):
        super().__init__(message)
        self.status = status


class _ListAvailableTags(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        registry = build_tag_registry()
        log.info("Available tags:")
        for category_name in sorted(registry.category_map.keys()):
            log.info(f"{category_name.capitalize()}:")
            category = registry.category_map[category_name]

            all_category_tags = sorted(category.tag_map.items())
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
        namespace: Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        if values is None:
            parser.print_help()
        else:
            tag_name = str(values)
            registry = build_tag_registry()
            tag_factory = registry.find_tag_factory(tag_name)
            if tag_factory is None:
                parser.exit(1, f"Could not find tag with '{tag_name}' name")
            log.info(tag_factory.configuration_signature)
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
            try:
                import importlib_metadata

                return importlib_metadata.version(package_name)
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


# CHECK: use pydantic-cli for argument parsing
def process_cli_configuration(argv: List[str]) -> RuntimeConfiguration:
    log.debug("Parsing command line arguments")
    parser = argparse.ArgumentParser(
        prog="tempren",
        description="Template-based renaming utility",
        fromfile_prefix_chars="@",
        add_help=False,
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
        "input_directory",
        type=existing_directory,
        help="Input directory where files to rename are stored",
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

    if args.conflict_stop:
        conflict_strategy = ConflictResolutionStrategy.stop
    elif args.conflict_ignore:
        conflict_strategy = ConflictResolutionStrategy.ignore
    elif args.conflict_override:
        conflict_strategy = ConflictResolutionStrategy.override
    elif args.conflict_manual:
        conflict_strategy = ConflictResolutionStrategy.manual
    else:
        conflict_strategy = ConflictResolutionStrategy.stop

    configuration = RuntimeConfiguration(
        template=args.template,
        input_directory=args.input_directory,
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


def user_conflict_resolver(
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


def main() -> int:
    configure_logging()
    argv = sys.argv[1:]
    try:
        config = process_cli_configuration(argv)
        registry = build_tag_registry()
        pipeline = build_pipeline(
            config, registry, manual_conflict_resolver=user_conflict_resolver
        )
        pipeline.execute()
        log.info("Done")
        return 0
    except SystemExitError as exc:
        if exc.status != 0:
            log.error(exc)
        return exc.status
    except TemplateEvaluationError as template_evaluation_error:
        render_template_evaluation_error(template_evaluation_error)
        return 5  # TODO: cleanup error codes
    except TemplateError as template_error:
        render_template_error(template_error)
        return 3
    except OSError as exc:
        log.error(f"Error: {exc}")
        return 4
    except InvalidDestinationError as exc:
        log.error(f"Error: {exc}")
        return 6


if __name__ == "__main__":
    sys.exit(main())
