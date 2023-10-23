from pathlib import Path

import pytest

from .conftest import CliTestsBase, ErrorCode, run_tempren


@pytest.mark.parametrize("sort_flag", ["-s", "--sort"])
class TestSortingFlags(CliTestsBase):
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
