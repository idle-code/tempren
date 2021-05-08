#!/usr/bin/env python
import argparse
import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, List, NoReturn, Optional, Sequence, Text, Union

from tempren.pipeline import RuntimeConfiguration, build_pipeline, build_tag_registry

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
        option_string: Optional[Text] = ...,
    ):
        registry = build_tag_registry()
        print("Available tags:")
        for tag_name, factory in registry.tag_registry.items():
            print(f"  {tag_name}\t{factory.__doc__}")
        parser.exit()


class _IncreaseLogVerbosity(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = ...,
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
    operation_mode = parser.add_mutually_exclusive_group(required=True)
    operation_mode.add_argument(
        "-n",
        "--name",
        action="store_true",
        help="Use template to generate file name",
    )
    operation_mode.add_argument(
        "-p",
        "--path",
        action="store_true",
        help="Use template to generate relative file path",
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
        "--list-tags",
        action=_ListAvailableTags,
        nargs=0,
        help="List available tags and exit",
    )

    # Upon parsing error, ArgumentParser tries to exit via calling `sys.exit()`.
    # We could catch resulting `SystemExit` exception but related error message still would be missing.
    # This behaviour is not comfortable for testing so here we monkeypatch exit method to
    # throw more practical exception instead.
    def throwing_exit(status: int = 0, message: Optional[str] = "") -> NoReturn:
        raise SystemExitError(status, message)

    parser.exit = throwing_exit  # type: ignore

    args = parser.parse_args(argv)

    return RuntimeConfiguration(**vars(args))


def main(argv: List[str]) -> int:
    try:
        log.debug("Parsing configuration")
        config = process_cli_configuration(argv)
        log.debug("Loading tags")
        registry = build_tag_registry()
        log.debug("Building pipeline")
        pipeline = build_pipeline(config, registry)

        log.debug("Executing pipeline")
        pipeline.execute()
        log.info("Done")
        return 0
    except SystemExitError as exc:
        if exc.status != 0:
            print(exc, file=sys.stderr, end="")
        return exc.status


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
