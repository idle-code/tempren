#!/usr/bin/env python
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import configargparse  # type: ignore
from tempren.pipeline import Pipeline


@dataclass
class RuntimeConfiguration:
    input_directory: Path
    name_template: Optional[str] = None
    path_template: Optional[str] = None
    dry_run: bool = False
    save_config: Optional[str] = None
    config: Optional[str] = None


def existing_directory(val: str) -> Path:
    directory_path = Path(val)
    if not directory_path.is_dir():
        raise configargparse.ArgumentTypeError(f"Directory '{val}' doesn't exists")
    return directory_path


class SystemExitError(Exception):
    status: int

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def parse_configuration(argv: List[str]) -> RuntimeConfiguration:
    parser = configargparse.ArgumentParser(
        prog="tempren", description="Template-based renaming utility."
    )
    operation_mode = parser.add_mutually_exclusive_group(required=True)
    operation_mode.add_argument(
        "-n",
        "--name-template",
        type=str,
        help="Template used to generate new filename string",
    )
    operation_mode.add_argument(
        "-p",
        "--path-template",
        type=str,
        help="Template used to generate new filepath string",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Do not perform any renaming - just show expected operation results",
    )
    parser.add_argument(
        "input_directory",
        type=existing_directory,
        help="Input directory where files to rename are stored",
    )
    parser.add_argument(
        "--save-config",
        is_write_out_config_file_arg=True,
        metavar="CONFIG",
        help="Save command line options to configuration file",
    )
    parser.add_argument(
        "-c", "--config", is_config_file_arg=True, help="Load configuration from file"
    )

    # Upon parsing error, ArgumentParser tries to exit via calling `sys.exit()`.
    # We could catch resulting `SystemExit` exception but related error message still would be missing.
    # This behaviour is not comfortable for testing so here we monkeypatch exit method to
    # throw more practical exception instead.
    def throwing_exit(status: int = 0, message: str = ""):
        raise SystemExitError(status, message)

    parser.exit = throwing_exit

    args = parser.parse_args(argv)
    config = RuntimeConfiguration(**vars(args))

    return config


def main(argv: List[str]) -> int:
    try:
        config = parse_configuration(argv)
        # TODO: Create builder to generate pipeline from RuntimeConfiguration
        # pipeline = CliPipelineBuilder.build_from_configuration(config)
        return 0
    except SystemExitError as exc:
        if exc.status != 0:
            print(exc, file=sys.stderr, end="")
        return exc.status


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
