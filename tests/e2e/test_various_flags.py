import re
from pathlib import Path

import pytest

from .conftest import (
    CliTestsBase,
    ErrorCode,
    make_relative,
    run_tempren,
    run_tempren_process,
)


class TestVariousFlags(CliTestsBase):
    def test_version(self):
        stdout, stderr, error_code = run_tempren("--version")

        assert error_code == ErrorCode.SUCCESS
        assert re.match(r"\d+\.\d+\.\d+", stdout)

    @pytest.mark.parametrize("flag", ["-d", "--dry-run"])
    def test_dry_run(self, text_data_dir: Path, flag: str):
        stdout, stderr, error_code = run_tempren(
            flag, "%Upper(){%Name()}", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "MARKDOWN.MD").exists()
        assert "HELLO.TXT" in stdout
        assert "MARKDOWN.MD" in stdout

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help(self, flag: str):
        stdout, stderr, error_code = run_tempren(flag)

        assert error_code == ErrorCode.SUCCESS
        assert "usage: tempren" in stdout

    def test_missing_template_and_input(self):
        stdout, stderr, error_code = run_tempren()

        assert error_code == ErrorCode.USAGE_ERROR
        assert "usage: tempren" in stderr

    def test_missing_input(self):
        stdout, stderr, error_code = run_tempren("%Upper(){%Name()}")

        assert error_code == ErrorCode.USAGE_ERROR
        assert "usage: tempren" in stderr

    @pytest.mark.parametrize("flag", ["-l", "--list-tags"])
    def test_list_tags(self, flag: str):
        stdout, stderr, error_code = run_tempren(flag)
        stdout_lines = list(map(str.strip, stdout.split("\n")))

        assert error_code == ErrorCode.SUCCESS
        assert any(filter(lambda line: re.match(r"^Count", line), stdout_lines))
        assert any(filter(lambda line: re.match(r"^Upper", line), stdout_lines))
        assert any(filter(lambda line: re.match(r"^Name", line), stdout_lines))

    @pytest.mark.parametrize("flag", ["-v", "--verbose"])
    def test_verbose_output(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "--list-tags")

        assert "Verbosity level set to" in stdout

    @pytest.mark.parametrize("flag", ["-q", "--quiet"])
    def test_quiet_output(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "--list-tags")

        assert not stdout

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help_nonexistent_tag_documentation(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "NonExistent")

        assert error_code == ErrorCode.USAGE_ERROR
        assert "Unknown tag name" in stderr
        assert "NonExistent" in stderr

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help_tag_documentation(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "Count")

        assert error_code == ErrorCode.SUCCESS
        assert "Count(start" in stdout
        assert "start - " in stdout
        assert "Generates sequential numbers" in stdout

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help_tag_in_category_documentation(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "Image.Width")

        assert error_code == ErrorCode.SUCCESS
        assert "Width()" in stdout

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help_tag_documentation_long_description(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "Dir")

        assert error_code == ErrorCode.SUCCESS
        assert "If context is present" in stdout

    def test_default_flat_traversal(self, nested_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", "%Upper(){%Name()}", nested_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (nested_data_dir / "LEVEL-1.FILE").exists()
        assert not (nested_data_dir / "first" / "LEVEL-2.FILE").exists()

    @pytest.mark.parametrize("flag", ["-r", "--recursive"])
    @pytest.mark.parametrize("pass_relative", [False, True])
    def test_recursive_traversal(
        self, flag: str, pass_relative: bool, nested_data_dir: Path
    ):
        nested_dir = (
            make_relative(nested_data_dir) if pass_relative else nested_data_dir
        )

        stdout, stderr, error_code = run_tempren_process(
            "--name", flag, "%Upper(){%Name()}", nested_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (nested_data_dir / "LEVEL-1.FILE").exists()
        assert (nested_data_dir / "first" / "LEVEL-2.FILE").exists()

    def test_default_hidden_files_handling(self, hidden_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", "%Upper(){%Name()}", hidden_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (hidden_data_dir / "VISIBLE.TXT").exists()
        assert not (hidden_data_dir / ".HIDDEN.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / "NESTED_VISIBLE.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / ".NESTED_HIDDEN.TXT").exists()

    @pytest.mark.parametrize("flag", ["-ih", "--include-hidden"])
    def test_hidden_files_inclusion(self, flag: str, hidden_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", flag, "%Upper(){%Name()}", hidden_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (hidden_data_dir / "VISIBLE.TXT").exists()
        assert (hidden_data_dir / ".HIDDEN.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / "NESTED_VISIBLE.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / ".NESTED_HIDDEN.TXT").exists()

    @pytest.mark.parametrize("flag", ["-ih", "--include-hidden"])
    def test_hidden_directories_inclusion(self, flag: str, hidden_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", "--recursive", flag, "%Upper(){%Name()}", hidden_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (hidden_data_dir / "VISIBLE.TXT").exists()
        assert (hidden_data_dir / ".HIDDEN.TXT").exists()
        assert (hidden_data_dir / ".hidden" / "NESTED_VISIBLE.TXT").exists()
        assert (hidden_data_dir / ".hidden" / ".NESTED_HIDDEN.TXT").exists()
