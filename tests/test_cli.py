from pathlib import Path

import pytest
from tempren.cli import RuntimeConfiguration, SystemExitError, parse_configuration


def parse_cli(*args) -> RuntimeConfiguration:
    args = list(map(str, args))
    return parse_configuration(args)


valid_name_template = "%Count().%Ext()"
valid_path_template = "%DirName()/%Count().%Ext()"


class TestCliParser:
    def test_nonexistent_input_directory(self, nonexistent_path: Path):
        with pytest.raises(SystemExitError) as exc:
            parse_cli("--name-template", valid_name_template, nonexistent_path)

        assert exc.match("doesn't exists")

    def test_require_template(self, text_data_dir: Path):
        with pytest.raises(SystemExitError) as exc:
            parse_cli(text_data_dir)

        assert exc.match("one of the arguments (.*)+template(.*)+ is required")

    def test_default_config_name_template(self, text_data_dir: Path):
        config = parse_cli("--name-template", valid_name_template, text_data_dir)

        assert config.name_template == valid_name_template
        assert config.path_template is None
        assert config.input_directory == text_data_dir
        assert not config.dry_run

    def test_default_config_path_template(self, text_data_dir: Path):
        config = parse_cli("--path-template", valid_path_template, text_data_dir)

        assert config.name_template is None
        assert config.path_template == valid_path_template
        assert config.input_directory == text_data_dir
        assert not config.dry_run

    def test_name_and_path_templates_are_mutually_exclusive(self, text_data_dir: Path):
        with pytest.raises(SystemExitError) as exc:
            parse_cli(
                "--name-template",
                valid_name_template,
                "--path-template",
                valid_path_template,
                text_data_dir,
            )

        assert exc.match("not allowed with argument")

    def test_config_save(self, tmp_path: Path, text_data_dir: Path):
        config_path = tmp_path / "test_config.ini"

        with pytest.raises(SystemExitError) as exc:
            parse_cli(
                "--name-template",
                valid_name_template,
                text_data_dir,
                "--save-config",
                config_path,
            )

        assert exc.value.status == 0
        assert config_path.exists()
