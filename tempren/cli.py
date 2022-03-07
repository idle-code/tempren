#!/usr/bin/env python
import argparse
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from textwrap import indent
from typing import Any, List, NoReturn, Optional, Sequence, Text, Union

from tempren.pipeline import (
    FilterType,
    OperationMode,
    RuntimeConfiguration,
    build_pipeline,
    build_tag_registry,
)
from tempren.template.tree_builder import TagTemplateError, TagTemplateSyntaxError

log = logging.getLogger("CLI")
logging.basicConfig(level=logging.WARNING)


def existing_directory(val: str) -> Path:
    directory_path = Path(val)
    if not directory_path.is_dir():
        raise argparse.ArgumentTypeError(f"Directory '{val}' doesn't exists")
    return directory_path


def existing_file(val: str) -> Path:
    file_path = Path(val)
    if not file_path.is_file():
        raise argparse.ArgumentTypeError(f"File '{val}' doesn't exists")
    return file_path


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
        print("Available tags:")
        all_tags = sorted(registry.tag_registry.items())
        max_name_length = max([len(tag_name) for tag_name, factory in all_tags])
        log.debug("Longest tag name: %d", max_name_length)
        for tag_name, factory in all_tags:
            print(f"  {tag_name.ljust(max_name_length)} - {factory.__doc__}")
        parser.exit()


class _ShowVersion(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ):
        print(self.find_package_version())
        parser.exit()

    @staticmethod
    def find_package_version() -> str:
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


# CHECK: use pydantic-cli for argument parsing
def process_cli_configuration(argv: List[str]) -> RuntimeConfiguration:
    parser = argparse.ArgumentParser(
        prog="tempren", description="Template-based renaming utility."
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Do not perform any renaming - just show expected operation results",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action=_IncreaseLogVerbosity,
        nargs=0,
        help="Increase logging verbosity",
    )
    operation_mode = parser.add_mutually_exclusive_group()
    # TODO: generate modes based on OperationMode
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
    parser.add_argument(
        "-ft",
        "--filter-type",
        choices=[e.value for e in FilterType],
        default=FilterType.regex,  # TODO: change to template when available
        help="Type of filter expression",
    )
    parser.add_argument(
        "-fi",
        "--filter-invert",
        action="store_true",
        help="Invert (negate) filter expression result",
    )
    parser.add_argument(
        "-f",
        "--filter",
        type=str,
        metavar="FILTER_EXPRESSION",
        help="Filter expression used to include individual files",
    )
    parser.add_argument(
        "-si",
        "--sort-invert",
        action="store_true",
        help="Reverse sorting order",
    )
    parser.add_argument(
        "-s",
        "--sort",
        type=str,
        metavar="SORT_EXPRESSION",
        help="Sorting expression used to order file list before processing",
    )
    parser.add_argument(
        "template",
        type=str,
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

    configuration = RuntimeConfiguration(**vars(args))

    return configuration


def render_template_error(template_error: TagTemplateError, indent_size: int = 4):
    assert template_error.location.line == 1, "Nu support for multiline templates yet"
    if template_error.location.length == 1:
        underline = " " * template_error.location.column + "^"
    else:
        underline = (
            " " * template_error.location.column + "~" * template_error.location.length
        )
    print()
    print(indent("\n".join((template_error.template, underline)), " " * indent_size))
    print(f"Template error at {template_error.location}: {template_error.message}")


def main() -> int:
    argv = sys.argv[1:]
    try:
        log.debug("Parsing configuration")
        config = process_cli_configuration(argv)
        log.debug("Loading tags")
        registry = build_tag_registry()
        log.debug("Building pipeline")
        pipeline = build_pipeline(config, registry)

        log.debug("Executing pipeline")
        log.info("Directory base: %s", config.input_directory)
        pipeline.execute()
        log.info("Done")
        return 0
    except SystemExitError as exc:
        if exc.status != 0:
            print(exc, file=sys.stderr, end="")
        return exc.status
    except TagTemplateError as template_error:
        render_template_error(template_error)
        return 3


if __name__ == "__main__":
    sys.exit(main())
