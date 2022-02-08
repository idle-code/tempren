from pathlib import Path

import pytest

from tempren.file_filters import RegexFilenameFileFilter, RegexPathFileFilter
from tempren.path_generator import File


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

    @pytest.mark.parametrize("invert", [False, True])
    def test_inversion_of_result(self, invert: bool):
        file_filter = RegexFilenameFileFilter(".*\\.ext$", invert=invert)

        assert file_filter(File(Path("name.EXT"))) == invert
        assert file_filter(File(Path("name.ext"))) != invert

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

    @pytest.mark.parametrize("invert", [False, True])
    def test_inversion_of_result(self, invert: bool):
        file_filter = RegexPathFileFilter("^foo", invert=invert)

        assert file_filter(File(Path("bar/foo.spam"))) == invert
        assert file_filter(File(Path("foo/bar.spam"))) != invert

    @pytest.mark.parametrize("ignore_case", [False, True])
    def test_case_insensitivity(self, ignore_case: bool):
        file_filter = RegexPathFileFilter("directory", ignore_case=ignore_case)

        assert file_filter(File(Path("directory/file.foo")))
        assert file_filter(File(Path("DIRECTORY/file.foo"))) == ignore_case
