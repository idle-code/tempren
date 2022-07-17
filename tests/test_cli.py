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

project_root_path = os.getcwd()


def run_tempren_process(*args) -> Tuple[str, str, int]:
    """Run tempren with provided arguments as separate process"""
    args = list(map(str, filter(lambda v: v is not None, args)))
    os.chdir(project_root_path)
    print("Running: tempren", " ".join(args))
    completed_process = subprocess.run(
        [sys.executable, "-m", "tempren.cli"] + args,
        capture_output=True,
    )

    return (
        completed_process.stdout.decode("utf-8"),
        completed_process.stderr.decode("utf-8"),
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
        cwd=project_root_path,
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


class TestVariousFlags:
    def test_version(self):
        stdout, stderr, error_code = run_tempren("--version")

        assert error_code == 0
        assert re.match(r"\d\.\d\.\d", stdout)

    @pytest.mark.parametrize("flag", ["-d", "--dry-run"])
    def test_dry_run(self, text_data_dir: Path, flag: str):
        stdout, stderr, error_code = run_tempren(
            flag, "%Upper(){%Name()}", text_data_dir
        )

        assert error_code == 0
        assert (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "MARKDOWN.MD").exists()
        assert "HELLO.TXT" in stdout
        assert "MARKDOWN.MD" in stdout

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help(self, flag: str):
        stdout, stderr, error_code = run_tempren(flag)

        assert error_code == 0
        assert "usage: tempren" in stdout

    def test_missing_template_and_input(self):
        stdout, stderr, error_code = run_tempren()

        assert error_code == 2
        assert "usage: tempren" in stderr

    def test_missing_input(self):
        stdout, stderr, error_code = run_tempren("%Upper(){%Name()}")

        assert error_code == 2
        assert "usage: tempren" in stderr

    @pytest.mark.parametrize("flag", ["-l", "--list-tags"])
    def test_list_tags(self, flag: str):
        stdout, stderr, error_code = run_tempren(flag)
        stdout_lines = list(map(str.strip, stdout.split("\n")))

        assert error_code == 0
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

        assert error_code == 1
        assert "Could not find tag with 'NonExistent' name" in stderr

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help_tag_documentation(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "Count")

        assert error_code == 0
        assert "Count(start" in stdout
        assert "start - " in stdout
        assert "Generates sequential numbers" in stdout

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_help_tag_documentation_long_description(self, flag: str):
        stdout, stderr, error_code = run_tempren_process(flag, "Dir")

        assert error_code == 0
        assert "If context is present" in stdout

    def test_default_flat_traversal(self, nested_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", "%Upper(){%Name()}", nested_data_dir
        )

        assert error_code == 0
        assert (nested_data_dir / "LEVEL-1.FILE").exists()
        assert not (nested_data_dir / "first" / "LEVEL-2.FILE").exists()

    @pytest.mark.parametrize("flag", ["-r", "--recursive"])
    def test_recursive_traversal(self, flag: str, nested_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", flag, "%Upper(){%Name()}", nested_data_dir
        )

        assert error_code == 0
        assert (nested_data_dir / "LEVEL-1.FILE").exists()
        assert (nested_data_dir / "first" / "LEVEL-2.FILE").exists()

    def test_default_hidden_files_handling(self, hidden_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", "%Upper(){%Name()}", hidden_data_dir
        )

        assert error_code == 0
        assert (hidden_data_dir / "VISIBLE.TXT").exists()
        assert not (hidden_data_dir / ".HIDDEN.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / "NESTED_VISIBLE.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / ".NESTED_HIDDEN.TXT").exists()

    @pytest.mark.parametrize("flag", ["-ih", "--include-hidden"])
    def test_hidden_files_inclusion(self, flag: str, hidden_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", flag, "%Upper(){%Name()}", hidden_data_dir
        )

        assert error_code == 0
        assert (hidden_data_dir / "VISIBLE.TXT").exists()
        assert (hidden_data_dir / ".HIDDEN.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / "NESTED_VISIBLE.TXT").exists()
        assert not (hidden_data_dir / ".hidden" / ".NESTED_HIDDEN.TXT").exists()

    @pytest.mark.parametrize("flag", ["-ih", "--include-hidden"])
    def test_hidden_directories_inclusion(self, flag: str, hidden_data_dir: Path):
        stdout, stderr, error_code = run_tempren_process(
            "--name", "--recursive", flag, "%Upper(){%Name()}", hidden_data_dir
        )

        assert error_code == 0
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

        assert error_code == 0
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

        assert error_code == 0
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

        assert error_code == 2
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

        assert error_code == 3
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

        assert error_code == 5
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

        assert error_code == 2
        assert "Non-empty argument required" in stderr

    def test_sorting(self, text_data_dir: Path, sort_flag: str):
        stdout, stderr, error_code = run_tempren(
            sort_flag,
            "%Size()",
            "%Count()%Ext()",
            text_data_dir,
        )

        assert error_code == 0
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

        assert error_code == 0
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

        assert error_code == 3
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

        assert error_code == 5
        assert "evaluation error occurred" in stderr


@pytest.mark.parametrize("name_mode_flag", ["-n", "--name", None])
class TestNameMode:
    def test_name_mode(self, text_data_dir: Path, name_mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            name_mode_flag, "%Upper(){%Name()}", text_data_dir
        )

        assert error_code == 0
        assert (text_data_dir / "HELLO.TXT").exists()
        assert (text_data_dir / "MARKDOWN.MD").exists()
        assert not (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "markdown.md").exists()

    def test_nonexistent_input(self, nonexistent_path: Path, name_mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            name_mode_flag, "%Upper(){%Name()}", nonexistent_path
        )

        assert error_code != 0
        assert "doesn't exists" in stderr

    @pytest.mark.parametrize(
        "name_expression", ["%UnknownTag()", "%MissingArgStart)", "%MissingArgEnd("]
    )
    def test_name_template_error(
        self, text_data_dir: Path, name_mode_flag: str, name_expression: str
    ):
        stdout, stderr, error_code = run_tempren(
            name_mode_flag, name_expression, text_data_dir
        )

        assert error_code == 3
        assert "Template error" in stderr

    def test_generated_name_contains_separator_error(
        self, text_data_dir: Path, name_mode_flag: str
    ):
        stdout, stderr, error_code = run_tempren(
            name_mode_flag, "subdir/%Name()", text_data_dir
        )

        assert error_code == 0
        assert "Invalid name generated for" in stderr
        assert "subdir/hello.txt" in stderr
        assert "subdir/markdown.md" in stderr


@pytest.mark.parametrize("path_mode_flag", ["-p", "--path"])
class TestPathMode:
    def test_path_mode(self, text_data_dir: Path, path_mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            path_mode_flag, "%Upper(){%Trim(-1,left){%Ext()}}/%Name()", text_data_dir
        )

        assert error_code == 0
        assert not (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "markdown.md").exists()
        assert (text_data_dir / "TXT" / "hello.txt").exists()
        assert (text_data_dir / "MD" / "markdown.md").exists()

    def test_nonexistent_input(self, nonexistent_path: Path, path_mode_flag: str):
        stdout, stderr, error_code = run_tempren(
            path_mode_flag, "%Upper(){%Name()}", nonexistent_path
        )

        assert error_code != 0
        assert "doesn't exists" in stderr

    @pytest.mark.parametrize(
        "path_expression", ["%UnknownTag()", "%MissingArgStart)", "%MissingArgEnd("]
    )
    def test_path_template_error(
        self, text_data_dir: Path, path_mode_flag: str, path_expression: str
    ):
        stdout, stderr, error_code = run_tempren(
            path_mode_flag, path_expression, text_data_dir
        )

        assert error_code == 3
        assert "Template error" in stderr

    @pytest.mark.parametrize("path_expression", ["../../%Name()", "/some/dir/%Name()"])
    def test_generated_path_outside_input_directory_error(
        self, text_data_dir: Path, path_mode_flag: str, path_expression: str
    ):
        stdout, stderr, error_code = run_tempren(
            path_mode_flag, path_expression, text_data_dir
        )

        assert error_code == 6
        assert "Path generated for" in stderr
        assert "is not relative to the input directory" in stderr


class TestConflictResolution:
    def test_transient_conflict_resolution(self, text_data_dir: Path):
        run_tempren("%Count(start=0)", text_data_dir)
        assert (text_data_dir / "0").exists()
        assert (text_data_dir / "1").exists()

        stdout, stderr, error_code = run_tempren(
            "--sort", "%Name()", "%Count(start=1)", text_data_dir
        )

        assert error_code == 0
        assert (text_data_dir / "1").exists()
        assert (text_data_dir / "2").exists()

    @pytest.mark.parametrize("flag", ["-cs", "--conflict-stop", None])
    def test_stop_conflict_resolution(self, text_data_dir: Path, flag: Optional[str]):
        stdout, stderr, error_code = run_tempren(
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        assert error_code != 0
        assert "Could not rename" in stderr
        assert "as destination path" in stderr
        assert "StaticFilename" in stderr
        assert not (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "markdown.md").exists()

    @pytest.mark.parametrize("flag", ["-ci", "--conflict-ignore"])
    def test_ignore_conflict_resolution(self, text_data_dir: Path, flag: str):
        stdout, stderr, error_code = run_tempren(
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        assert error_code == 0
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

        assert error_code == 0
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
        assert error_code != 0
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
        assert error_code == 0
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
            flag, "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        stdout, stderr = tempren_process.communicate(input=selection + "\n", timeout=3)
        assert "StaticFilename" in stderr
        assert "already existing file" in stderr

        error_code = tempren_process.wait()
        assert error_code == 0
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
        assert error_code == 0
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
        assert error_code != 0
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
