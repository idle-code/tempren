import io
import os
import re
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Optional, Tuple

import pytest

import tempren.cli
from tempren.cli import ErrorCode

project_root_path = os.getcwd()

# Both tests and tempren process manipulate CurrentWorkingDirectory setting.
# Following environment allows for running tempren out of the main repository directory.
tempren_process_env = os.environ.copy()
tempren_process_env["PYTHONPATH"] = ":".join(
    [project_root_path, tempren_process_env.get("PYTHONPATH", "")]
)


def run_tempren_process(*args) -> Tuple[str, str, int]:
    """Run tempren with provided arguments as separate process"""
    args = list(map(str, filter(lambda v: v is not None, args)))
    print("CWD:", os.getcwd())
    print("COMMAND: tempren", " ".join(args))
    completed_process = subprocess.run(
        [sys.executable, "-m", "tempren.cli"] + args,
        capture_output=True,
        env=tempren_process_env,
    )

    captured_stdout = completed_process.stdout.decode("utf-8")
    print("STDOUT:\n" + captured_stdout)
    captured_stderr = completed_process.stderr.decode("utf-8")
    print("STDERR:\n" + captured_stderr)
    return (
        captured_stdout,
        captured_stderr,
        completed_process.returncode,
    )


def start_tempren_process(*args) -> subprocess.Popen:
    """Run tempren with provided arguments as separate process"""
    args = list(map(str, filter(lambda v: v is not None, args)))
    # CHECK: Use pexpect?
    # print("Running: tempren", " ".join(args))
    tempren_process = subprocess.Popen(
        [sys.executable, "-m", "tempren.cli"] + args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=tempren_process_env,
        bufsize=1,
        universal_newlines=True,
    )
    return tempren_process


def run_tempren(*args) -> Tuple[str, str, int]:
    """Run tempren's main() function with provided arguments"""
    args = list(map(str, filter(lambda v: v is not None, args)))
    old_sys_argv = sys.argv.copy()
    sys.argv[1:] = args
    print("Running: tempren", " ".join(args))
    try:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                error_code = tempren.cli.main()
    finally:
        sys.argv = old_sys_argv

    return stdout.getvalue(), stderr.getvalue(), error_code


def make_relative(path: Path) -> Path:
    os.chdir(path.parent)
    cwd = os.getcwd()
    return path.relative_to(cwd)


class TestVariousFlags:
    def test_version(self):
        stdout, stderr, error_code = run_tempren("--version")

        assert error_code == ErrorCode.SUCCESS
        assert re.match(r"\d\.\d\.\d", stdout)

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


@pytest.mark.parametrize("invert_flag", ["-fi", "--filter-invert", None])
class TestNameFilterFlags:
    @pytest.mark.parametrize("flag", ["-fg", "--filter-glob"])
    def test_glob_filter(
        self, flag: str, invert_flag: Optional[str], text_data_dir: Path
    ):
        self._test_filter_type(flag, "*.txt", invert_flag, text_data_dir)

    @pytest.mark.parametrize("flag", ["-fr", "--filter-regex"])
    def test_regex_filter(
        self, flag: str, invert_flag: Optional[str], text_data_dir: Path
    ):
        self._test_filter_type(flag, r".*\.txt$", invert_flag, text_data_dir)

    @pytest.mark.parametrize("flag", ["-ft", "--filter-template"])
    def test_template_filter(
        self, flag: str, invert_flag: Optional[str], text_data_dir: Path
    ):
        self._test_filter_type(flag, "%Size() < 50", invert_flag, text_data_dir)

    def _test_filter_type(
        self,
        flag: str,
        expression: str,
        invert_flag: Optional[str],
        text_data_dir: Path,
    ):
        stdout, stderr, error_code = run_tempren(
            flag,
            expression,
            invert_flag,
            "%Upper(){%Name()}",
            text_data_dir,
        )

        assert error_code == ErrorCode.SUCCESS
        if invert_flag is None:
            assert (text_data_dir / "HELLO.TXT").exists()
            assert not (text_data_dir / "MARKDOWN.MD").exists()
            assert not (text_data_dir / "hello.txt").exists()
            assert (text_data_dir / "markdown.md").exists()
        else:
            assert not (text_data_dir / "HELLO.TXT").exists()
            assert (text_data_dir / "MARKDOWN.MD").exists()
            assert (text_data_dir / "hello.txt").exists()
            assert not (text_data_dir / "markdown.md").exists()


@pytest.mark.parametrize("invert_flag", ["-fi", "--filter-invert", None])
class TestPathFilterFlags:
    @pytest.mark.parametrize("flag", ["-fg", "--filter-glob"])
    def test_glob_filter(
        self, flag: str, invert_flag: Optional[str], nested_data_dir: Path
    ):
        self._test_filter_type(flag, "**/*-3.file", invert_flag, nested_data_dir)

    @pytest.mark.parametrize("flag", ["-fr", "--filter-regex"])
    def test_regex_filter(
        self, flag: str, invert_flag: Optional[str], nested_data_dir: Path
    ):
        self._test_filter_type(
            flag, r"^second/third/.*\.file", invert_flag, nested_data_dir
        )

    @pytest.mark.parametrize("flag", ["-ft", "--filter-template"])
    def test_template_filter(
        self, flag: str, invert_flag: Optional[str], nested_data_dir: Path
    ):
        self._test_filter_type(flag, "%Size() > 30", invert_flag, nested_data_dir)

    def _test_filter_type(
        self,
        flag: str,
        expression: str,
        invert_flag: Optional[str],
        nested_data_dir: Path,
    ):
        stdout, stderr, error_code = run_tempren(
            "--recursive",
            "--path",
            flag,
            expression,
            invert_flag,
            "%Dir()/%Upper(){%Name()}",
            nested_data_dir,
        )

        assert error_code == ErrorCode.SUCCESS
        if invert_flag is None:
            assert not (nested_data_dir / "second" / "third" / "level-3.file").exists()
            assert (nested_data_dir / "second" / "third" / "LEVEL-3.FILE").exists()
            assert (nested_data_dir / "first" / "level-2.file").exists()
            assert not (nested_data_dir / "first" / "LEVEL-2.FILE").exists()
        else:
            assert (nested_data_dir / "second" / "third" / "level-3.file").exists()
            assert not (nested_data_dir / "second" / "third" / "LEVEL-3.FILE").exists()
            assert not (nested_data_dir / "first" / "level-2.file").exists()
            assert (nested_data_dir / "first" / "LEVEL-2.FILE").exists()


@pytest.mark.parametrize("flag", ["-ft", "--filter-template"])
class TestFilterTemplateErrors:
    def test_empty_filtering_template(self, flag: str, nonexistent_path: Path):
        stdout, stderr, error_code = run_tempren(
            flag,
            "",
            "%Count()%Ext()",
            nonexistent_path,
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "Non-empty argument required" in stderr

    @pytest.mark.parametrize("filter_expression", ["%UnknownTag()", "%Size"])
    def test_filter_template_error(
        self, flag: str, filter_expression: str, text_data_dir: Path
    ):
        stdout, stderr, error_code = run_tempren(
            flag,
            filter_expression,
            "%Count()%Ext()",
            text_data_dir,
        )

        assert error_code == ErrorCode.TEMPLATE_SYNTAX_ERROR
        assert "Template error" in stderr

    @pytest.mark.parametrize("filter_expression", ["%Size() + 'foobar'"])
    def test_filter_template_evaluation_error(
        self, flag: str, filter_expression: str, text_data_dir: Path
    ):
        stdout, stderr, error_code = run_tempren(
            flag,
            filter_expression,
            "%Count()%Ext()",
            text_data_dir,
        )

        assert error_code == ErrorCode.TEMPLATE_EVALUATION_ERROR
        assert "evaluation error occurred" in stderr


@pytest.mark.parametrize("sort_flag", ["-s", "--sort"])
class TestSortingFlags:
    def test_empty_sorting_template(self, nonexistent_path: Path, sort_flag: str):
        stdout, stderr, error_code = run_tempren(
            sort_flag,
            "",
            "%Count()%Ext()",
            nonexistent_path,
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "Non-empty argument required" in stderr

    def test_sorting(self, text_data_dir: Path, sort_flag: str):
        stdout, stderr, error_code = run_tempren(
            sort_flag,
            "%Size()",
            "%Count()%Ext()",
            text_data_dir,
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "0.txt").exists()
        assert (text_data_dir / "1.md").exists()

    @pytest.mark.parametrize("invert_flag", ["-si", "--sort-invert"])
    def test_inverted_sorting(
        self, text_data_dir: Path, invert_flag: str, sort_flag: str
    ):
        stdout, stderr, error_code = run_tempren(
            invert_flag,
            sort_flag,
            "%Size()",
            "%Count()%Ext()",
            text_data_dir,
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "0.md").exists()
        assert (text_data_dir / "1.txt").exists()

    @pytest.mark.parametrize("sort_expression", ["%UnknownTag()", "%Size,"])
    def test_sort_template_error(
        self, text_data_dir: Path, sort_flag: str, sort_expression: str
    ):
        stdout, stderr, error_code = run_tempren(
            sort_flag,
            sort_expression,
            "%Count()%Ext()",
            text_data_dir,
        )

        assert error_code == ErrorCode.TEMPLATE_SYNTAX_ERROR
        assert "Template error" in stderr

    @pytest.mark.parametrize("sort_expression", ["%Size() + 'foobar'", ","])
    def test_sort_template_evaluation_error(
        self, sort_flag: str, sort_expression: str, text_data_dir: Path
    ):
        stdout, stderr, error_code = run_tempren(
            sort_flag,
            sort_expression,
            "%Count()%Ext()",
            text_data_dir,
        )

        assert error_code == ErrorCode.TEMPLATE_EVALUATION_ERROR
        assert "evaluation error occurred" in stderr


class CommonModeTestsBase:
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


class TestConflictResolution:
    def test_transient_conflict_resolution(self, text_data_dir: Path):
        run_tempren("%Count(start=0)", text_data_dir)
        assert (text_data_dir / "0").exists()
        assert (text_data_dir / "1").exists()

        stdout, stderr, error_code = run_tempren(
            "--sort", "%Name()", "%Count(start=1)", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "1").exists()
        assert (text_data_dir / "2").exists()

    @pytest.mark.parametrize("flag", ["-cs", "--conflict-stop", None])
    def test_stop_conflict_resolution(self, text_data_dir: Path, flag: Optional[str]):
        stdout, stderr, error_code = run_tempren(
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        assert error_code == ErrorCode.INVALID_DESTINATION_ERROR
        assert "Could not rename" in stderr
        assert "as destination path" in stderr
        assert "StaticFilename" in stderr
        assert not (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "markdown.md").exists()

    @pytest.mark.parametrize("flag", ["-ci", "--conflict-ignore"])
    def test_ignore_conflict_resolution(self, text_data_dir: Path, flag: str):
        stdout, stderr, error_code = run_tempren(
            flag, "--verbose", "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert "Skipping renaming of" in stdout
        assert "as destination path already exists" in stdout
        assert "StaticFilename" in stdout
        assert not (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "markdown.md").exists()

    @pytest.mark.parametrize("flag", ["-co", "--conflict-override"])
    def test_override_conflict_resolution(self, text_data_dir: Path, flag: str):
        stdout, stderr, error_code = run_tempren(
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert "Overriding destination" in stderr
        assert "StaticFilename" in stderr
        assert not (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "markdown.md").exists()
        assert (text_data_dir / "StaticFilename").exists()

    @pytest.mark.parametrize("selection", ["stop", "s", "sto", "STOP"])
    @pytest.mark.parametrize("flag", ["-cm", "--conflict-manual"])
    def test_manual_conflict_resolution_stop(
        self, text_data_dir: Path, flag: str, selection: str
    ):
        tempren_process = start_tempren_process(
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        stdout, stderr = tempren_process.communicate(input=selection + "\n", timeout=3)
        assert "StaticFilename" in stderr
        assert "already existing file" in stderr

        error_code = tempren_process.wait()
        assert error_code == ErrorCode.INVALID_DESTINATION_ERROR
        assert "Could not rename" in stderr
        assert "as destination path" in stderr
        assert "StaticFilename" in stderr
        assert not (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "markdown.md").exists()

    @pytest.mark.parametrize("selection", ["override", "o", "over", "OVE"])
    @pytest.mark.parametrize("flag", ["-cm", "--conflict-manual"])
    def test_manual_conflict_resolution_override(
        self, text_data_dir: Path, flag: str, selection: str
    ):
        tempren_process = start_tempren_process(
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        stdout, stderr = tempren_process.communicate(input=selection + "\n", timeout=3)
        assert "StaticFilename" in stderr
        assert "already existing file" in stderr

        error_code = tempren_process.wait()
        assert error_code == ErrorCode.SUCCESS
        assert "Overriding destination" in stderr
        assert "StaticFilename" in stderr
        assert not (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "markdown.md").exists()
        assert (text_data_dir / "StaticFilename").exists()

    @pytest.mark.parametrize("selection", ["ignore", "i", "ign", "IGNO", ""])
    @pytest.mark.parametrize("flag", ["-cm", "--conflict-manual"])
    def test_manual_conflict_resolution_ignore(
        self, text_data_dir: Path, flag: str, selection: str
    ):
        tempren_process = start_tempren_process(
            flag, "--verbose", "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        stdout, stderr = tempren_process.communicate(input=selection + "\n", timeout=3)
        assert "StaticFilename" in stderr
        assert "already existing file" in stderr

        error_code = tempren_process.wait()
        assert error_code == ErrorCode.SUCCESS
        assert "Skipping renaming of" in stdout
        assert "as destination path already exists" in stdout
        assert "StaticFilename" in stdout
        assert not (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "markdown.md").exists()

    @pytest.mark.parametrize(
        "selection", ["custom path", "c", "custom", "cus", "CUSTO"]
    )
    @pytest.mark.parametrize("flag", ["-cm", "--conflict-manual"])
    def test_manual_conflict_resolution_custom_name(
        self, text_data_dir: Path, flag: str, selection: str
    ):
        tempren_process = start_tempren_process(
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        stdout, stderr = tempren_process.communicate(
            input=selection + "\n" + "UserProvidedName" + "\n", timeout=3
        )
        assert "StaticFilename" in stderr
        assert "already existing file" in stderr
        assert "Custom path" in stdout

        error_code = tempren_process.wait()
        assert error_code == ErrorCode.SUCCESS
        assert not (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "StaticFilename").exists()
        assert not (text_data_dir / "markdown.md").exists()
        assert (text_data_dir / "UserProvidedName").exists()

    def test_manual_conflict_resolution_custom_name_already_exists(
        self, text_data_dir: Path
    ):
        tempren_process = start_tempren_process(
            "--conflict-manual",
            "--sort",
            "%Name()",
            "StaticFilename",
            text_data_dir,
        )

        stdout, stderr = tempren_process.communicate(
            input="custom\n" + "StaticFilename\n", timeout=3
        )
        assert "Could not rename" in stderr
        assert "already exists" in stderr

        error_code = tempren_process.wait()
        assert error_code == ErrorCode.INVALID_DESTINATION_ERROR
        assert not (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "markdown.md").exists()

    def test_manual_conflict_resolution_invalid_choice(self, text_data_dir: Path):
        tempren_process = start_tempren_process(
            "--conflict-manual",
            "--sort",
            "%Name()",
            "StaticFilename",
            text_data_dir,
        )

        stdout, stderr = tempren_process.communicate(
            input="foobar\nignore\n", timeout=3
        )
        assert "Invalid choice" in stderr
        assert "foobar" in stderr

        tempren_process.wait()


@pytest.mark.parametrize("flag", ["-ah", "--ad-hoc"])
class TestAdHocTags:
    def test_nonexistent_command(self, flag: str, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "unknown_command", "%Sanitize{%cut('-c', '3')}_%Name()", text_data_dir
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "unknown_command" in stderr

    @pytest.mark.parametrize("custom_name", [False, True])
    def test_tag_from_standard_command(
        self, flag: str, custom_name: bool, text_data_dir: Path
    ):
        if custom_name:
            stdout, stderr, error_code = run_tempren(
                flag, "Cut=cut", "%Sanitize{%Cut('-c', '3')}_%Name()", text_data_dir
            )
        else:
            stdout, stderr, error_code = run_tempren(
                flag, "cut", "%Sanitize{%cut('-c', '3')}_%Name()", text_data_dir
            )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "l_hello.txt").exists()
        assert (text_data_dir / "Tr c_markdown.md").exists()

    @pytest.mark.parametrize("custom_name", [False, True])
    def test_tag_from_script(
        self, flag: str, custom_name: bool, tags_data_dir: Path, text_data_dir: Path
    ):
        script_path = tags_data_dir / "my_script.sh"
        if custom_name:
            stdout, stderr, error_code = run_tempren(
                flag, f"MyScript={script_path}", "%MyScript()_%Name()", text_data_dir
            )
        else:
            stdout, stderr, error_code = run_tempren(
                flag, script_path, "%my_script()_%Name()", text_data_dir
            )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "1_hello.txt").exists()
        assert (text_data_dir / "3_markdown.md").exists()

    def test_multiple_tags(self, flag: str, tags_data_dir: Path, text_data_dir: Path):
        script_path = tags_data_dir / "my_script.sh"
        stdout, stderr, error_code = run_tempren(
            flag,
            f"First={script_path}",
            flag,
            f"Second={script_path}",
            "%First()%Second()_%Name()",
            text_data_dir,
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "11_hello.txt").exists()
        assert (text_data_dir / "33_markdown.md").exists()

    def test_multiple_tags_same_name(
        self, flag: str, tags_data_dir: Path, text_data_dir: Path
    ):
        script_path = tags_data_dir / "my_script.sh"
        stdout, stderr, error_code = run_tempren(
            flag,
            f"Same={script_path}",
            flag,
            f"Same=cut",
            "%Same()_%Name()",
            text_data_dir,
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "Same" in stderr
        assert "cut" in stderr
        assert "my_script.sh" in stderr

    def test_invalid_tag_name(self, flag: str, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            flag,
            f"Cut.Me=cut",
            "%Cut.Me()_%Name()",
            text_data_dir,
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "'Cut.Me' cannot be used as tag name" in stderr

    def test_invalid_exec_name(self, flag: str):
        pass

    def test_documentation(self, flag: str):
        pass
