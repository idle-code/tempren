#!/usr/bin/env python
import argparse
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from textwrap import indent
from typing import Any, List, NoReturn, Optional, Sequence, Text, Union

from .pipeline import (
    FilterType,
    OperationMode,
    RuntimeConfiguration,
    build_pipeline,
    build_tag_registry,
)
from .template.tree_builder import TagTemplateError

log = logging.getLogger("CLI")
logging.basicConfig(level=logging.WARNING)


def existing_directory(val: str) -> Path:
    directory_path = Path(val)
    if not directory_path.is_dir():
        raise argparse.ArgumentTypeError(f"Directory '{val}' doesn't exists")
    return directory_path


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
        for category_name in sorted(registry.category_map.keys()):
            print(f"{category_name.capitalize()}:")
            category = registry.category_map[category_name]

            all_category_tags = sorted(category.tag_map.items())
            max_name_length = max(
                [len(tag_name) for tag_name, factory in all_category_tags]
            )
            log.debug(
                "Longest tag name: %d in category %s", max_name_length, category_name
            )
            for tag_name, factory in all_category_tags:
                print(
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
            print(tag_factory.configuration_signature)
            print()
            print(tag_factory.short_description)
            if tag_factory.long_description:
                print()
                print(tag_factory.long_description)

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
        log.info("Verbosity level set to %d", root_logger.level)


# CHECK: use pydantic-cli for argument parsing
def process_cli_configuration(argv: List[str]) -> RuntimeConfiguration:
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
        "-v",
        "--verbose",
        action=_IncreaseLogVerbosity,
        nargs=0,
        help="Increase logging verbosity",
    )

    operation_modes_group = parser.add_argument_group("operation modes")
    operation_mode = operation_modes_group.add_mutually_exclusive_group()
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
        type=str,
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
        type=str,
        metavar="sort_expression",
        help="Sorting expression used to order file list before processing",
    )
    sorting_group.add_argument(
        "-si",
        "--sort-invert",
        action="store_true",
        help="Reverse sorting order",
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

    configuration = RuntimeConfiguration(
        template=args.template,
        input_directory=args.input_directory,
        dry_run=args.dry_run,
        filter_type=filter_type,
        filter=filter_expression,
        filter_invert=args.filter_invert,
        sort_invert=args.sort_invert,
        sort=args.sort,
        mode=args.mode,
    )

    return configuration


def render_template_error(template_error: TagTemplateError, indent_size: int = 4):
    assert template_error.location.line == 1, "No support for multiline templates yet"
    if template_error.location.length == 1:
        underline = " " * template_error.location.column + "^"
    else:
        underline = (
            " " * template_error.location.column + "~" * template_error.location.length
        )
    print(file=sys.stderr)
    print(
        indent("\n".join((template_error.template, underline)), " " * indent_size),
        file=sys.stderr,
    )
    print(
        f"Template error at {template_error.location}: {template_error.message}",
        file=sys.stderr,
    )


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
