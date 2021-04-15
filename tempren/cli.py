#!/usr/bin/env python
import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import configargparse  # type: ignore

from tempren.filesystem import FileGatherer, Renamer
from tempren.pipeline import Pipeline
from tempren.template.name_generators import TemplateNameGenerator
from tempren.template.tree_builder import TagRegistry, TagTreeBuilder

log = logging.getLogger("CLI")
logging.basicConfig(level=logging.DEBUG)


@dataclass
class RuntimeConfiguration:
    input_directory: Path
    name_template: Optional[str] = None
    path_template: Optional[str] = None
    dry_run: bool = False
    save_config: Optional[str] = None
    config: Optional[str] = None


class ConfigurationError(Exception):
    pass


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
    # parser = configargparse.ArgumentParser(
    #     prog="tempren", description="Template-based renaming utility."
    # )
    parser = argparse.ArgumentParser(
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
    # parser.add_argument(
    #     "--save-config",
    #     is_write_out_config_file_arg=True,
    #     metavar="CONFIG",
    #     help="Save command line options to configuration file",
    # )
    # parser.add_argument(
    #     "-c", "--config", is_config_file_arg=True, help="Load configuration from file"
    # )

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


def build_tag_registry() -> TagRegistry:
    registry = TagRegistry()
    return registry


# TODO: Move to pipeline.py
def build_pipeline(config: RuntimeConfiguration) -> Pipeline:
    registry = build_tag_registry()

    pipeline = Pipeline()
    pipeline.file_gatherer = FileGatherer(config.input_directory)
    tree_builder = TagTreeBuilder()

    if config.name_template:
        bound_pattern = registry.bind(tree_builder.parse(config.name_template))
        pipeline.name_generator = TemplateNameGenerator(bound_pattern)
    elif config.path_template:
        raise ConfigurationError()  # pipeline.path_generator = TemplateNameGenerator(registry, config.path_template)
    else:
        raise ConfigurationError()
    pipeline.renamer = Renamer()
    return pipeline


def main(argv: List[str]) -> int:
    try:
        log.debug("Parsing configuration")
        config = parse_configuration(argv)
        log.debug("Building pipeline")
        pipeline = build_pipeline(config)
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
