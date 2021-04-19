#!/usr/bin/env python
import argparse
import logging
from pathlib import Path
from typing import List, NoReturn, Optional

from pydantic import BaseModel

from tempren.filesystem import FileGatherer, PrintingOnlyRenamer, Renamer
from tempren.pipeline import Pipeline
from tempren.template.path_generators import (
    TemplateNameGenerator,
    TemplatePathGenerator,
)
from tempren.template.tree_builder import TagRegistry, TagTreeBuilder

log = logging.getLogger("CLI")
logging.basicConfig(level=logging.DEBUG)


class RuntimeConfiguration(BaseModel):
    input_directory: Path
    name_template: Optional[str] = None
    path_template: Optional[str] = None
    dry_run: bool = False
    save_config: Optional[Path] = None
    config: Optional[Path] = None


class ConfigurationError(Exception):
    pass


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


# CHECK: use pydantic-cli for argument parsing
def process_cli_configuration(argv: List[str]) -> RuntimeConfiguration:
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
    parser.add_argument(
        "--save-config",
        metavar="CONFIG",
        help="Save command line options to configuration file",
    )
    parser.add_argument(
        "-c", "--config", type=existing_file, help="Load configuration from file"
    )

    # Upon parsing error, ArgumentParser tries to exit via calling `sys.exit()`.
    # We could catch resulting `SystemExit` exception but related error message still would be missing.
    # This behaviour is not comfortable for testing so here we monkeypatch exit method to
    # throw more practical exception instead.
    def throwing_exit(status: int = 0, message: Optional[str] = "") -> NoReturn:
        raise SystemExitError(status, message)

    parser.exit = throwing_exit  # type: ignore

    args = parser.parse_args(argv)

    config = RuntimeConfiguration(**vars(args))
    if config.config:
        log.info(f"Reading configuration from {config.config}")
        config_from_file = RuntimeConfiguration.parse_file(config.config)
        log.debug(f"Configuration read from file: {config_from_file.json()}")
        config = RuntimeConfiguration(**config_from_file.dict(), **vars(args))

    if config.save_config:
        log.info(f"Saving configuration to {config.save_config}")
        with open(config.save_config, "w") as config_file:
            config_file.write(config.json(indent=4))
        raise SystemExitError(0, f"Configuration was saved to: {config.save_config}")
    # TODO: handle save configuration
    return config


def build_tag_registry() -> TagRegistry:
    import tempren.plugins.tags.core
    import tempren.plugins.tags.text

    registry = TagRegistry()
    registry.register_tag(tempren.plugins.tags.core.CountTag)
    registry.register_tag(tempren.plugins.tags.core.ExtTag)
    registry.register_tag(tempren.plugins.tags.core.DirnameTag)
    registry.register_tag(tempren.plugins.tags.core.FilenameTag)
    registry.register_tag(tempren.plugins.tags.text.UnidecodeTag)
    return registry


# TODO: Move to pipeline.py
def build_pipeline(config: RuntimeConfiguration) -> Pipeline:
    registry = build_tag_registry()

    pipeline = Pipeline()
    # TODO: specify base_path
    pipeline.file_gatherer = iter(FileGatherer(config.input_directory))
    tree_builder = TagTreeBuilder()

    if config.name_template:
        bound_pattern = registry.bind(tree_builder.parse(config.name_template))
        pipeline.path_generator = TemplateNameGenerator(
            config.input_directory, bound_pattern
        )
    elif config.path_template:
        bound_pattern = registry.bind(tree_builder.parse(config.path_template))
        pipeline.path_generator = TemplatePathGenerator(
            config.input_directory, bound_pattern
        )
    else:
        raise ConfigurationError()

    if config.dry_run:
        pipeline.renamer = PrintingOnlyRenamer()
    else:
        pipeline.renamer = Renamer()
    return pipeline


def main(argv: List[str]) -> int:
    try:
        log.debug("Parsing configuration")
        config = process_cli_configuration(argv)
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
