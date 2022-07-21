from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.core import (
    BaseTag,
    CountTag,
    DirTag,
    ExtTag,
    MimeExtTag,
    MimeTag,
    NameTag,
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

    def test_zero_width_results_in_integer(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(width=0)

        result = tag.process(nonexistent_file, None)

        assert isinstance(result, int)

    def test_positive_width_results_in_string(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(width=3)

        result = tag.process(nonexistent_file, None)

        assert isinstance(result, str)

    def test_first_result_is_start(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(start=123)

        result = tag.process(nonexistent_file, None)

        assert result == 123

    def test_second_result_differs_by_step(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(step=3)

        tag.process(nonexistent_file, None)
        result = tag.process(nonexistent_file, None)

        assert result == 3

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

    def test_step_below_zero(self, nonexistent_file: File):
        tag = CountTag()
        tag.configure(start=0, step=-1)

        result = tag.process(nonexistent_file, None)
        assert result == 0

        with pytest.raises(ValueError):
            tag.process(nonexistent_file, None)

    def test_per_directory_counters(self, nonexistent_absolute_path: Path):
        tag = CountTag()
        tag.configure()
        dir1_file = File(nonexistent_absolute_path, Path("dir1") / "file1")
        dir2_file = File(nonexistent_absolute_path, Path("dir2") / "file2")

        result = tag.process(dir1_file, None)
        assert result == 0

        result = tag.process(dir2_file, None)
        assert result == 0

    def test_global_counter(self, nonexistent_absolute_path: Path):
        tag = CountTag()
        tag.configure(common=True)
        dir1_file = File(nonexistent_absolute_path, Path("dir1") / "file1")
        dir2_file = File(nonexistent_absolute_path, Path("dir2") / "file2")

        result = tag.process(dir1_file, None)
        assert result == 0

        result = tag.process(dir2_file, None)
        assert result == 1


class TestExtTag:
    def test_without_context_original_extension_is_used(self):
        tag = ExtTag()

        extension = tag.process(File.from_path("/test/file.foo"), None)

        assert extension == ".foo"

    def test_no_extension_on_filename(self):
        tag = ExtTag()

        extension = tag.process(File.from_path("/test/file"), None)

        assert extension == ""

    def test_context_extension(self, nonexistent_file: File):
        tag = ExtTag()

        extension = tag.process(nonexistent_file, "test/file.bar")

        assert extension == ".bar"

    def test_multiple_extensions(self, nonexistent_file: File):
        tag = ExtTag()

        extension = tag.process(nonexistent_file, "test/file.bar.spam")

        assert extension == ".spam"  # TODO: Check if this is desired behaviour


class TestBaseTag:
    def test_without_context_original_basename_is_used(self):
        tag = BaseTag()

        basename = tag.process(File.from_path("/test/file.foo"), None)

        assert basename == "file"

    def test_no_extension_on_filename(self):
        tag = BaseTag()

        basename = tag.process(File.from_path("/test/filename"), None)

        assert basename == "filename"

    def test_context_basename(self, nonexistent_file: File):
        tag = BaseTag()

        basename = tag.process(nonexistent_file, "test/file.bar")

        assert basename == "file"

    def test_multiple_extensions(self, nonexistent_file: File):
        tag = BaseTag()

        basename = tag.process(nonexistent_file, "test/file.bar.spam")

        assert basename == "file.bar"  # TODO: Check if this is desired behaviour


class TestDirTag:
    def test_no_context(self, nonexistent_absolute_path: Path):
        tag = DirTag()
        file = File(nonexistent_absolute_path, Path("dir/file.name"))

        dirname = tag.process(file, None)

        assert dirname == Path("dir")

    def test_no_parent_dir(self, nonexistent_absolute_path: Path):
        tag = DirTag()
        file = File(nonexistent_absolute_path, Path("file.name"))

        dirname = tag.process(file, None)

        assert dirname == Path(".")

    def test_context_extension(self, nonexistent_file: File):
        tag = DirTag()

        dirname = tag.process(nonexistent_file, "bar/file")

        assert dirname == Path("bar")


class TestNameTag:
    def test_no_context(self):
        tag = NameTag()

        filename = tag.process(File.from_path("/test/file.name"), None)

        assert filename == "file.name"

    def test_context_filename(self, nonexistent_file: File):
        tag = NameTag()

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


class TestMimeTag:
    def test_mp3_mime_type(self, audio_data_dir: Path):
        tag = MimeTag()
        file = File(audio_data_dir, Path("sample.mp3"))

        mime_type = tag.process(file, None)

        assert mime_type == "audio/mpeg"

    def test_text_mime_type(self, text_data_dir: Path):
        tag = MimeTag()
        file = File(text_data_dir, Path("hello.txt"))

        mime_type = tag.process(file, None)

        assert mime_type == "text/plain"

    def test_just_type(self, text_data_dir: Path):
        tag = MimeTag()
        tag.configure(type=True)
        file = File(text_data_dir, Path("hello.txt"))

        mime_type = tag.process(file, None)

        assert mime_type == "text"

    def test_just_subtype(self, text_data_dir: Path):
        tag = MimeTag()
        tag.configure(subtype=True)
        file = File(text_data_dir, Path("hello.txt"))

        mime_type = tag.process(file, None)

        assert mime_type == "plain"

    def test_just_type_and_subtype(self, text_data_dir: Path):
        tag = MimeTag()
        tag.configure(type=True, subtype=True)
        file = File(text_data_dir, Path("hello.txt"))

        mime_type = tag.process(file, None)

        assert mime_type == "text/plain"


class TestMimeExtTag:
    def test_text_plain_extension(self, text_data_dir: Path):
        tag = MimeExtTag()
        file = File(text_data_dir, Path("hello.txt"))

        extension = tag.process(file, None)

        assert extension == ".txt"

    def test_audio_flac_extension(self, audio_data_dir: Path):
        tag = MimeExtTag()
        file = File(audio_data_dir, Path("sample.flac"))

        extension = tag.process(file, None)

        assert extension == ".flac"

    def test_audio_mpeg_extension(self, audio_data_dir: Path):
        tag = MimeExtTag()
        file = File(audio_data_dir, Path("sample.mp3"))

        extension = tag.process(file, None)

        assert extension == ".mp3"
