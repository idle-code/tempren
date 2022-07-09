from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.core import (
    BasenameTag,
    CountTag,
    DirnameTag,
    ExtTag,
    FilenameTag,
    SanitizeTag,
)


class TestCountTag:
    def test_accepts_no_context(self):
        tag = CountTag()

        assert not tag.require_context

    def test_negative_start(self):
        tag = CountTag()

        with pytest.raises(ValueError):
            tag.configure(start=-1)

    def test_zero_step(self):
        tag = CountTag()

        with pytest.raises(ValueError):
            tag.configure(step=0)

    def test_negative_width(self):
        tag = CountTag()

        with pytest.raises(ValueError):
            tag.configure(width=-1)

    def test_first_result_is_start(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(start=123)

        result = tag.process(nonexistent_file, None)

        assert result == "123"

    def test_second_result_differs_by_step(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(step=3)

        tag.process(nonexistent_file, None)
        result = tag.process(nonexistent_file, None)

        assert result == "3"

    def test_width_control_leading_zeros(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(width=3)

        result = tag.process(nonexistent_file, None)

        assert result == "000"

    def test_width_overflow(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(step=123, width=2)

        result = tag.process(nonexistent_file, None)
        assert result == "00"

        result = tag.process(nonexistent_file, None)
        assert result == "123"


class TestExtTag:
    def test_without_context_original_extension_is_used(self):
        tag = ExtTag()

        extension = tag.process(File.from_path("/test/file.foo"), None)

        assert extension == "foo"

    def test_no_extension_on_filename(self):
        tag = ExtTag()

        extension = tag.process(File.from_path("/test/file"), None)

        assert extension == ""

    def test_context_extension(self, nonexistent_file: File):
        tag = ExtTag()

        extension = tag.process(nonexistent_file, "test/file.bar")

        assert extension == "bar"

    def test_multiple_extensions(self, nonexistent_file: File):
        tag = ExtTag()

        extension = tag.process(nonexistent_file, "test/file.bar.spam")

        assert extension == "spam"  # TODO: Check if this is desired behaviour


class TestBasenameTag:
    def test_without_context_original_basename_is_used(self):
        tag = BasenameTag()

        basename = tag.process(File.from_path("/test/file.foo"), None)

        assert basename == "file"

    def test_no_extension_on_filename(self):
        tag = BasenameTag()

        basename = tag.process(File.from_path("/test/filename"), None)

        assert basename == "filename"

    def test_context_basename(self, nonexistent_file: File):
        tag = BasenameTag()

        basename = tag.process(nonexistent_file, "test/file.bar")

        assert basename == "file"

    def test_multiple_extensions(self, nonexistent_file: File):
        tag = BasenameTag()

        basename = tag.process(nonexistent_file, "test/file.bar.spam")

        assert basename == "file.bar"  # TODO: Check if this is desired behaviour


class TestDirnameTag:
    def test_no_context(self):
        tag = DirnameTag()
        file = File(Path("/test"), Path("/test/dir/file.name"))

        dirname = tag.process(file, None)

        assert dirname == "dir"

    def test_no_parent_dir(self):
        tag = DirnameTag()
        file = File(Path("/test"), Path("/test/file.name"))

        dirname = tag.process(file, None)

        assert dirname == "."

    def test_context_extension(self, nonexistent_file: File):
        tag = DirnameTag()

        dirname = tag.process(nonexistent_file, "bar/file")

        assert dirname == "bar"


class TestFilenameTag:
    def test_no_context(self):
        tag = FilenameTag()

        filename = tag.process(File.from_path("/test/file.name"), None)

        assert filename == "file.name"

    def test_context_filename(self, nonexistent_file: File):
        tag = FilenameTag()

        filename = tag.process(nonexistent_file, "test/file.name")

        assert filename == "file.name"


class TestSanitizeTag:
    def test_no_special_chars(self, nonexistent_file: File):
        tag = SanitizeTag()

        filename = tag.process(nonexistent_file, "simple_filename.txt")

        assert filename == "simple_filename.txt"

    def test_special_chars(self, nonexistent_file: File):
        tag = SanitizeTag()

        filename = tag.process(nonexistent_file, r"fi:l*en" "a?m>e|.t<xt")

        assert filename == "filename.txt"

    def test_path_separators(self, nonexistent_file: File):
        tag = SanitizeTag()

        filename = tag.process(nonexistent_file, "path\\to/file")

        assert filename == "path/to/file"
