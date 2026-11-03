import io
from pathlib import Path

import pytest

from .conftest import CliTestsBase, ErrorCode, run_tempren, start_tempren_process


class TestConflictResolution(CliTestsBase):
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
    def test_stop_conflict_resolution(self, text_data_dir: Path, flag: str | None):
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

        stdout, stderr = tempren_process.communicate(input=selection + "\n", timeout=10)
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

        stdout, stderr = tempren_process.communicate(input=selection + "\n", timeout=10)
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

        stdout, stderr = tempren_process.communicate(input=selection + "\n", timeout=10)
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
            input=selection + "\n" + "UserProvidedName" + "\n", timeout=10
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
            input="custom\n" + "StaticFilename\n", timeout=10
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
            input="foobar\nignore\n", timeout=10
        )
        assert "Invalid choice" in stderr
        assert "foobar" in stderr

        tempren_process.wait()

    def test_transient_conflict_resolution_with_multiple_input_directories(
        self, text_data_dir: Path, nested_data_dir: Path, tmp_path: Path, monkeypatch
    ):
        run_tempren("%Count(start=0)", text_data_dir)
        assert (text_data_dir / "0").exists()
        assert (text_data_dir / "1").exists()
        # Run from a directory unrelated to any of the input directories
        monkeypatch.chdir(tmp_path)

        # "0" -> "1" in the first directory is deferred (transient conflict) and has
        # to be retried after files from the second directory were processed
        stdout, stderr, error_code = run_tempren(
            "--sort",
            "%Name()",
            "%Count(start=1)",
            text_data_dir,
            nested_data_dir,
        )

        assert error_code == ErrorCode.SUCCESS
        assert sorted(p.name for p in text_data_dir.iterdir()) == ["1", "2"]
        assert (nested_data_dir / "1").is_file()
        assert not (nested_data_dir / "level-1.file").exists()

    def test_manual_conflict_resolution_relative_custom_path(
        self, text_data_dir: Path, tmp_path: Path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.stdin", io.StringIO("custom\nUserProvidedName\n"))

        stdout, stderr, error_code = run_tempren(
            "--conflict-manual", "--sort", "%Name()", "StaticFilename", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "UserProvidedName").exists()
        assert not (tmp_path / "UserProvidedName").exists()
