from pathlib import Path

import pytest

from .conftest import CliTestsBase, ErrorCode, make_relative, run_tempren


class CommonModeTestsBase(CliTestsBase):
    def test_nonexistent_input(self, nonexistent_path: Path, mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            mode_flag, "%Upper(){%Name()}", nonexistent_path
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "doesn't exists" in stderr

    @pytest.mark.parametrize(
        "expression", ["%UnknownTag()", "%MissingArgStart)", "%MissingArgEnd("]
    )
    def test_template_error(self, text_data_dir: Path, mode_flag: str, expression: str):
        stdout, stderr, error_code = run_tempren(mode_flag, expression, text_data_dir)

        assert error_code == ErrorCode.TEMPLATE_SYNTAX_ERROR
        assert "Template error" in stderr

    def test_same_name_generated(self, text_data_dir: Path, mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            mode_flag, "-s", "%Name()", "%Name()", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert "Skipping renaming" in stdout
        assert "hello.txt" in stdout
        assert "source and destination are the same" in stdout

    @pytest.mark.parametrize("pass_relative", [False, True])
    def test_multiple_directories_can_be_passed(
        self,
        text_data_dir: Path,
        nested_data_dir: Path,
        mode_flag: str,
        pass_relative: bool,
    ):
        assert text_data_dir.parent == nested_data_dir.parent
        first_directory = (
            make_relative(text_data_dir) if pass_relative else text_data_dir
        )
        second_directory = (
            make_relative(nested_data_dir) if pass_relative else nested_data_dir
        )

        stdout, stderr, error_code = run_tempren(
            mode_flag, "%Name()|%Upper()", first_directory, second_directory
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "HELLO.TXT").exists()
        assert (nested_data_dir / "LEVEL-1.FILE").exists()

    @pytest.mark.parametrize("pass_relative", [False, True])
    def test_explicit_files_can_be_passed(
        self, nested_data_dir: Path, mode_flag: str, pass_relative: bool
    ):
        nested_dir = (
            make_relative(nested_data_dir) if pass_relative else nested_data_dir
        )

        files = [
            nested_dir / "level-1.file",
            nested_dir / "first" / "level-2.file",
        ]
        stdout, stderr, error_code = run_tempren(mode_flag, "%Name()|%Upper()", *files)

        assert error_code == ErrorCode.SUCCESS
        assert (nested_data_dir / "LEVEL-1.FILE").exists()
        assert (nested_data_dir / "first" / "LEVEL-2.FILE").exists()


@pytest.mark.parametrize("mode_flag", ["-n", "--name", None])
class TestNameMode(CommonModeTestsBase):
    def test_name_mode(self, text_data_dir: Path, mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            mode_flag, "%Upper(){%Name()}", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "HELLO.TXT").exists()
        assert (text_data_dir / "MARKDOWN.MD").exists()
        assert not (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "markdown.md").exists()

    def test_generated_name_contains_separator_error(
        self, text_data_dir: Path, mode_flag: str
    ):
        stdout, stderr, error_code = run_tempren(
            mode_flag, "-s", "%Name()", "subdir/%Name()", text_data_dir
        )

        assert error_code == ErrorCode.INVALID_DESTINATION_ERROR
        assert "Invalid name generated for" in stderr
        assert "subdir/hello.txt" in stderr


@pytest.mark.parametrize("mode_flag", ["-p", "--path"])
class TestPathMode(CommonModeTestsBase):
    def test_path_mode(self, text_data_dir: Path, mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            mode_flag, "%Upper(){%Trim(-1,left){%Ext()}}/%Name()", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert not (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "markdown.md").exists()
        assert (text_data_dir / "TXT" / "hello.txt").exists()
        assert (text_data_dir / "MD" / "markdown.md").exists()

    @pytest.mark.parametrize("path_expression", ["../../%Name()", "/some/dir/%Name()"])
    def test_generated_path_outside_input_directory_error(
        self, text_data_dir: Path, mode_flag: str, path_expression: str
    ):
        stdout, stderr, error_code = run_tempren(
            mode_flag, path_expression, text_data_dir
        )

        assert error_code == ErrorCode.INVALID_DESTINATION_ERROR
        assert "Path generated for" in stderr
        assert "is not relative to the input directory" in stderr

    def test_explicit_files_use_parent_as_input_directory(
        self, nested_data_dir: Path, mode_flag: str
    ):
        files = [
            nested_data_dir / "level-1.file",
            nested_data_dir / "first" / "level-2.file",
        ]
        stdout, stderr, error_code = run_tempren(mode_flag, "subdir/%Name()", *files)

        assert error_code == ErrorCode.SUCCESS
        assert (nested_data_dir / "subdir" / "level-1.file").exists()
        assert (nested_data_dir / "first" / "subdir" / "level-2.file").exists()
