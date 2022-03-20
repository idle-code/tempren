import io
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import List, Tuple

import pytest

from tempren.cli import RuntimeConfiguration, SystemExitError, process_cli_configuration
from tempren.pipeline import OperationMode


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
        assert config.mode == OperationMode.name
        assert config.input_directory == text_data_dir
        assert not config.dry_run

    def test_default_config_path_template(self, text_data_dir: Path):
        config = process_cli("--path", valid_path_template, text_data_dir)

        assert config.template == valid_path_template
        assert config.mode == OperationMode.path
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


def run_tempren(*args) -> Tuple[str, str, int]:
    from tempren.cli import main

    old_sys_argv = sys.argv.copy()
    sys.argv[1:] = list(map(str, args))
    try:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                error_code = main()
    finally:
        sys.argv = old_sys_argv

    return stdout.getvalue(), stderr.getvalue(), error_code


class TestVariousFlags:
    def test_version(self, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren("--version")

        assert re.match(r"\d\.\d\.\d", stdout)
        assert error_code == 0

    def test_dry_run_long(self, text_data_dir: Path):
        run_tempren("--dry-run", "%Upper(){%Filename()}", text_data_dir)

        assert (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "MARKDOWN.MD").exists()

    def test_dry_run_short(self, text_data_dir: Path):
        run_tempren("-d", "%Upper(){%Filename()}", text_data_dir)

        assert (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "MARKDOWN.MD").exists()

    def test_help_long(self, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren("--help")

        assert "usage: tempren" in stdout
        assert error_code == 0

    def test_help_short(self, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren("-h")

        assert "usage: tempren" in stdout
        assert error_code == 0

    def test_missing_template_and_input(self, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren()

        assert "usage: tempren" in stderr
        assert error_code == 2

    def test_missing_input(self, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren("%Upper(){%Filename()}")

        assert "usage: tempren" in stderr
        assert error_code == 2

    def test_default_mode(self, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren("%Upper(){%Filename()}", text_data_dir)

        assert error_code == 0
        assert (text_data_dir / "HELLO.TXT").exists()
        assert (text_data_dir / "MARKDOWN.MD").exists()
        assert not (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "markdown.md").exists()
