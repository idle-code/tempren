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
    def test_empty_filter_matches_everything(self):
        file_filter = RegexFilenameFileFilter("")
        file = File(Path("some/file.name"))

        assert file_filter(file)

    def test_filter_matches_just_filename(self):
        file_filter = RegexFilenameFileFilter("^file.*")

        assert not file_filter(File(Path("file/name.ext")))
        assert file_filter(File(Path("file/filename.ext")))

    def test_filter_matches_from_beginning(self):
        file_filter = RegexFilenameFileFilter("file")

        assert file_filter(File(Path("file.ext")))
        assert file_filter(File(Path("filename.ext")))

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(self, ignore_case: bool):
        file_filter = RegexFilenameFileFilter(".*\\.ext$", ignore_case=ignore_case)

        assert file_filter(File(Path("name.ext")))
        assert file_filter(File(Path("name.EXT"))) == ignore_case


class TestRegexPathFileFilter:
    def test_empty_filter_matches_everything(self):
        file_filter = RegexPathFileFilter("")
        file = File(Path("some/file.name"))

        assert file_filter(file)

    def test_filter_matches_whole_path(self):
        file_filter = RegexPathFileFilter("^file.*")

        assert file_filter(File(Path("file/name.ext")))
        assert file_filter(File(Path("file/filename.ext")))

    def test_filter_matches_from_beginning(self):
        file_filter = RegexPathFileFilter("file")

        assert file_filter(File(Path("file/path.ext")))
        assert file_filter(File(Path("filename/path.ext")))

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(self, ignore_case: bool):
        file_filter = RegexPathFileFilter("directory", ignore_case=ignore_case)

        assert file_filter(File(Path("directory/file.foo")))
        assert file_filter(File(Path("DIRECTORY/file.foo"))) == ignore_case


class TestGlobFilenameFileFilter:
    def test_empty_filter_matches_nothing(self):
        file_filter = GlobFilenameFileFilter("")
        file = File(Path("some/file.name"))

        assert not file_filter(file)

    def test_star_filter_matches_everything(self):
        file_filter = GlobFilenameFileFilter("*")
        file = File(Path("some/file.name"))

        assert file_filter(file)

    def test_filter_matches_just_filename(self):
        file_filter = GlobFilenameFileFilter("file*")

        assert not file_filter(File(Path("file/name.ext")))
        assert file_filter(File(Path("file/filename.ext")))

    def test_filter_matches_from_beginning(self):
        file_filter = GlobFilenameFileFilter("file*")

        assert file_filter(File(Path("file.ext")))
        assert file_filter(File(Path("filename.ext")))

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(self, ignore_case: bool):
        file_filter = GlobFilenameFileFilter("*.ext", ignore_case=ignore_case)

        assert file_filter(File(Path("name.ext")))
        assert file_filter(File(Path("name.EXT"))) == ignore_case


class TestGlobPathFileFilter:
    def test_empty_filter_matches_nothing(self):
        file_filter = GlobPathFileFilter("")
        file = File(Path("some/file.name"))

        assert not file_filter(file)

    def test_star_filter_matches_everything(self):
        file_filter = GlobPathFileFilter("*")
        file = File(Path("some/file.name"))

        assert file_filter(file)

    def test_filter_matches_whole_path(self):
        file_filter = GlobPathFileFilter("file*")

        assert file_filter(File(Path("file/name.ext")))
        assert file_filter(File(Path("file/filename.ext")))

    def test_filter_matches_from_beginning(self):
        file_filter = GlobPathFileFilter("file*")

        assert file_filter(File(Path("file/path.ext")))
        assert file_filter(File(Path("filename/path.ext")))

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(self, ignore_case: bool):
        file_filter = GlobPathFileFilter("directory*", ignore_case=ignore_case)

        assert file_filter(File(Path("directory/file.foo")))
        assert file_filter(File(Path("DIRECTORY/file.foo"))) == ignore_case


class TestFileFilterInverter:
    @pytest.mark.parametrize("original_value", [False, True])
    def test_original_value_is_negated(self, original_value: bool):
        def original_filter(f: File) -> bool:
            return original_value

        inverted_filter = FileFilterInverter(original_filter)
        file = File(Path("some/file.name"))

        assert original_value == (not inverted_filter(file))


class TestTemplateFileFilter:
    @pytest.mark.parametrize("expression_text", ["", "$%", "1 +", "while True: pass"])
    def test_invalid_expression(self, expression_text: str, nonexistent_path: Path):
        pattern = Pattern([RawText(expression_text)])
        file_filter = TemplateFileFilter(pattern)
        file = File(nonexistent_path)

        with pytest.raises(SyntaxError):
            file_filter(file)

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
        self, expression_text: str, expected_result: bool, nonexistent_path: Path
    ):
        pattern = Pattern([RawText(expression_text)])
        file_filter = TemplateFileFilter(pattern)
        file = File(nonexistent_path)

        assert file_filter(file) == expected_result

    def test_file_is_passed_to_tags(self, nonexistent_path: Path):
        mock_tag = MockTag()
        mock_tag.process_output = "True"
        pattern = Pattern([TagInstance(tag=mock_tag)])
        file_filter = TemplateFileFilter(pattern)

        file_filter(File(nonexistent_path))

        assert mock_tag.path == nonexistent_path

    def test_tag_output_rendering(self, nonexistent_path: Path):
        mock_tag = MockTag()
        mock_tag.process_output = "foobar"
        pattern = Pattern([TagInstance(tag=mock_tag), RawText(".startswith('foo')")])
        file_filter = TemplateFileFilter(pattern)

        assert file_filter(File(nonexistent_path))

    def test_path_rendering(self, nonexistent_path: Path):
        mock_tag = MockTag()
        mock_tag.process_output = nonexistent_path
        pattern = Pattern([TagInstance(tag=mock_tag), RawText(".exists()")])
        file_filter = TemplateFileFilter(pattern)

        assert not file_filter(File(nonexistent_path))
