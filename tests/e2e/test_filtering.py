from pathlib import Path
from typing import Optional

import pytest

from .conftest import CliTestsBase, ErrorCode, run_tempren


@pytest.mark.parametrize("invert_flag", ["-fi", "--filter-invert", None])
class TestNameFilterFlags(CliTestsBase):
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
class TestPathFilterFlags(CliTestsBase):
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
class TestFilterTemplateErrors(CliTestsBase):
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
