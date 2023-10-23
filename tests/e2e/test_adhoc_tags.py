from pathlib import Path

import pytest

from .conftest import CliTestsBase, ErrorCode, run_tempren


@pytest.mark.parametrize("flag", ["-ah", "--ad-hoc"])
class TestAdHocTags(CliTestsBase):
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

    @pytest.mark.parametrize("custom_name", [False, True])
    def test_documentation(self, flag: str, custom_name: bool, tags_data_dir: Path):
        script_path = tags_data_dir / "my_script.sh"
        if custom_name:
            stdout, stderr, error_code = run_tempren(
                flag, f"MyScript={script_path}", "--help", "MyScript"
            )
        else:
            stdout, stderr, error_code = run_tempren(
                flag, script_path, "--help", "my_script"
            )

        assert error_code == ErrorCode.SUCCESS
        assert str(script_path) in stdout
        assert str(script_path.absolute()) in stdout
