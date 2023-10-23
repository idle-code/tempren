from pathlib import Path

import pytest

from .conftest import CliTestsBase, ErrorCode, run_tempren


@pytest.mark.parametrize("flag", ["-a", "--alias"])
class TestTagAliases(CliTestsBase):
    def test_alias_without_name(self, flag: str, nonexistent_path: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "FooBar", "%Name()", nonexistent_path
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "Missing alias name" in stderr

    def test_alias_without_pattern(self, flag: str, nonexistent_path: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "FooBar=", "%Name()", nonexistent_path
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "Missing alias pattern" in stderr

    def test_invalid_alias_name(self, flag: str, nonexistent_path: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "Foo.Bar=Spam", "%Name()", nonexistent_path
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "'Foo.Bar' cannot be used as tag name" in stderr

    def test_constant_alias(self, flag: str, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "Foo=Bar", "%Foo()_%Name()", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "Bar_hello.txt").exists()
        assert (text_data_dir / "Bar_markdown.md").exists()

    def test_single_tag_alias(self, flag: str, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "N=%Name()", "%N()", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "hello.txt").exists()
        assert (text_data_dir / "markdown.md").exists()

    def test_pattern_alias(self, flag: str, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "NU=%Name()|%Upper()", "%NU()", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "HELLO.TXT").exists()
        assert (text_data_dir / "MARKDOWN.MD").exists()

    def test_multiple_aliases_same_name(self, flag: str, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "Foo=Bar", flag, "Foo=Spam", "%Foo()_%Name()", text_data_dir
        )

        assert error_code == ErrorCode.USAGE_ERROR
        assert "Bar" in stderr
        assert "Spam" in stderr
        assert "Foo" in stderr

    def test_multiple_aliases(self, flag: str, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            flag, "Foo=Bar", flag, "Bar=Foo", "%Bar()%Foo()_%Name()", text_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert (text_data_dir / "FooBar_hello.txt").exists()
        assert (text_data_dir / "FooBar_markdown.md").exists()

    def test_documentation(self, flag: str):
        stdout, stderr, error_code = run_tempren(
            flag, "Original=%Name()", "--help", "Original"
        )

        assert error_code == ErrorCode.SUCCESS
        assert "%Name()" in stdout
        assert "Original" in stdout
        assert "Alias" in stdout
