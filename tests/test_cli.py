from pathlib import Path

import pytest

from tempren.cli import RuntimeConfiguration, SystemExitError, process_cli_configuration


def process_cli(*args) -> RuntimeConfiguration:
    args = list(map(str, args))
    return process_cli_configuration(args)


valid_name_template = "%Count().%Ext()"
valid_path_template = "%DirName()/%Count().%Ext()"


class TestCliParser:
    def test_require_template(self):
        with pytest.raises(SystemExitError) as exc:
            process_cli()

        assert exc.match("arguments are required: template")

    def test_nonexistent_input_directory(self, nonexistent_path: Path):
        with pytest.raises(SystemExitError) as exc:
            process_cli("--name", valid_name_template, nonexistent_path)

        assert exc.match("doesn't exists")

    def test_require_input_directory(self):
        with pytest.raises(SystemExitError) as exc:
            process_cli(valid_name_template)

        assert exc.match("arguments are required: input_directory")

    def test_default_config_name_template(self, text_data_dir: Path):
        config = process_cli("--name", valid_name_template, text_data_dir)

        assert config.template == valid_name_template
        assert config.name and not config.path
        assert config.input_directory == text_data_dir
        assert not config.dry_run

    def test_default_config_path_template(self, text_data_dir: Path):
        config = process_cli("--path", valid_path_template, text_data_dir)

        assert config.template == valid_path_template
        assert not config.name and config.path
        assert config.input_directory == text_data_dir
        assert not config.dry_run

    def test_name_and_path_templates_are_mutually_exclusive(self, text_data_dir: Path):
        with pytest.raises(SystemExitError) as exc:
            process_cli(
                "--name",
                "--path",
                valid_name_template,
                text_data_dir,
            )

        assert exc.match("not allowed with argument")
