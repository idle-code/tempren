from pathlib import Path

import pytest

from tempren.file_filters import (
    FileFilterInverter,
    GlobFilenameFileFilter,
    GlobPathFileFilter,
    RegexFilenameFileFilter,
    RegexPathFileFilter,
    TemplateFileFilter,
)
from tempren.path_generator import File
from tempren.template.tree_elements import Pattern, RawText, TagInstance

from .template.mocks import MockTag


class TestRegexFilenameFileFilter:
    def test_empty_filter_matches_everything(self, nonexistent_absolute_path: Path):
        file_filter = RegexFilenameFileFilter("")
        file = File(nonexistent_absolute_path, Path("file.name"))

        assert file_filter(file)

    def test_filter_matches_just_filename(self):
        file_filter = RegexFilenameFileFilter("^file.*")

        assert not file_filter(File.from_path("/file/name.ext"))
        assert file_filter(File.from_path("/file/filename.ext"))

    def test_filter_matches_from_beginning(self):
        file_filter = RegexFilenameFileFilter("file")

        assert file_filter(File.from_path("/file.ext"))
        assert file_filter(File.from_path("/filename.ext"))

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(
        self, ignore_case: bool, nonexistent_absolute_path: Path
    ):
        file_filter = RegexFilenameFileFilter(".*\\.ext$", ignore_case=ignore_case)

        assert file_filter(File(nonexistent_absolute_path, Path("name.ext")))
        assert (
            file_filter(File(nonexistent_absolute_path, Path("name.EXT")))
            == ignore_case
        )


class TestRegexPathFileFilter:
    def test_empty_filter_matches_everything(self, nonexistent_absolute_path: Path):
        file_filter = RegexPathFileFilter("")
        file = File(nonexistent_absolute_path, Path("some/file.name"))

        assert file_filter(file)

    def test_filter_matches_whole_relative_path(self, nonexistent_absolute_path: Path):
        file_filter = RegexPathFileFilter("^file.*")

        assert file_filter(File(nonexistent_absolute_path, Path("file") / "name.ext"))
        assert file_filter(
            File(nonexistent_absolute_path, Path("file") / "filename.ext")
        )

    def test_filter_matches_from_beginning(self, nonexistent_absolute_path: Path):
        file_filter = RegexPathFileFilter("file")

        assert file_filter(File(nonexistent_absolute_path, Path("file") / "path.ext"))
        assert file_filter(
            File(nonexistent_absolute_path, Path("filename") / "path.ext")
        )

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(
        self, ignore_case: bool, nonexistent_absolute_path: Path
    ):
        file_filter = RegexPathFileFilter("directory", ignore_case=ignore_case)

        assert file_filter(
            File(nonexistent_absolute_path, Path("directory") / "file.foo")
        )
        assert (
            file_filter(File(nonexistent_absolute_path, Path("DIRECTORY") / "file.foo"))
            == ignore_case
        )


class TestGlobFilenameFileFilter:
    def test_empty_filter_matches_nothing(self):
        file_filter = GlobFilenameFileFilter("")
        file = File.from_path("/some/file.name")

        assert not file_filter(file)

    def test_star_filter_matches_everything(self):
        file_filter = GlobFilenameFileFilter("*")
        file = File.from_path("/some/file.name")

        assert file_filter(file)

    def test_filter_matches_just_filename(self):
        file_filter = GlobFilenameFileFilter("file*")
        input_directory = Path("/file")

        assert not file_filter(File(input_directory, Path("name.ext")))
        assert file_filter(File(input_directory, Path("filename.ext")))

    def test_filter_matches_from_beginning(self):
        file_filter = GlobFilenameFileFilter("file*")
        input_directory = Path("/file")

        assert file_filter(File(input_directory, Path("file.ext")))
        assert file_filter(File(input_directory, Path("filename.ext")))

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(self, ignore_case: bool):
        file_filter = GlobFilenameFileFilter("*.ext", ignore_case=ignore_case)

        assert file_filter(File.from_path("/name.ext"))
        assert file_filter(File.from_path("/name.EXT")) == ignore_case


class TestGlobPathFileFilter:
    def test_empty_filter_matches_nothing(self):
        file_filter = GlobPathFileFilter("")
        file = File.from_path("/some/file.name")

        assert not file_filter(file)

    def test_star_filter_matches_everything(self):
        file_filter = GlobPathFileFilter("*")
        file = File.from_path("/some/file.name")

        assert file_filter(file)

    def test_filter_matches_whole_path(self, nonexistent_absolute_path: Path):
        file_filter = GlobPathFileFilter("file*")

        assert file_filter(File(nonexistent_absolute_path, Path("file/name.ext")))
        assert file_filter(File(nonexistent_absolute_path, Path("file/filename.ext")))

    def test_filter_matches_from_beginning(self, nonexistent_absolute_path: Path):
        file_filter = GlobPathFileFilter("file*")

        assert file_filter(File(nonexistent_absolute_path, Path("file/path.ext")))
        assert file_filter(File(nonexistent_absolute_path, Path("filename/path.ext")))

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(
        self, ignore_case: bool, nonexistent_absolute_path: Path
    ):
        file_filter = GlobPathFileFilter("directory*", ignore_case=ignore_case)

        assert file_filter(File(nonexistent_absolute_path, Path("directory/file.foo")))
        assert (
            file_filter(File(nonexistent_absolute_path, Path("DIRECTORY/file.foo")))
            == ignore_case
        )


class TestFileFilterInverter:
    @pytest.mark.parametrize("original_value", [False, True])
    def test_original_value_is_negated(
        self, original_value: bool, nonexistent_file: File
    ):
        def original_filter(f: File) -> bool:
            return original_value

        inverted_filter = FileFilterInverter(original_filter)

        assert original_value == (not inverted_filter(nonexistent_file))


class TestTemplateFileFilter:
    @pytest.mark.parametrize("expression_text", ["", "$%", "1 +", "while True: pass"])
    def test_invalid_expression(self, expression_text: str, nonexistent_file: File):
        pattern = Pattern([RawText(expression_text)])
        file_filter = TemplateFileFilter(pattern)

        with pytest.raises(SyntaxError):
            file_filter(nonexistent_file)

    @pytest.mark.parametrize(
        "expression_text,expected_result",
        [
            ("True", True),
            ("False", False),
            ("1", True),
            ("0", False),
            ("''", False),
            ("1 > 2", False),
            ("1 < 2", True),
            ("'PNG' == 'png' or len('PNG') == 3", True),
        ],
    )
    def test_valid_expression(
        self, expression_text: str, expected_result: bool, nonexistent_file: File
    ):
        pattern = Pattern([RawText(expression_text)])
        file_filter = TemplateFileFilter(pattern)

        assert file_filter(nonexistent_file) == expected_result

    def test_file_is_passed_to_tags(self, nonexistent_file: File):
        mock_tag = MockTag()
        mock_tag.process_output = "True"
        pattern = Pattern([TagInstance(tag=mock_tag)])
        file_filter = TemplateFileFilter(pattern)

        file_filter(nonexistent_file)

        assert mock_tag.file == nonexistent_file

    def test_tag_output_rendering(self, nonexistent_file: File):
        mock_tag = MockTag()
        mock_tag.process_output = "foobar"
        pattern = Pattern([TagInstance(tag=mock_tag), RawText(".startswith('foo')")])
        file_filter = TemplateFileFilter(pattern)

        assert file_filter(nonexistent_file)

    def test_path_rendering(self, nonexistent_file: File):
        mock_tag = MockTag()
        mock_tag.process_output = nonexistent_file.relative_path
        pattern = Pattern([TagInstance(tag=mock_tag), RawText(".exists()")])
        file_filter = TemplateFileFilter(pattern)

        assert not file_filter(nonexistent_file)
