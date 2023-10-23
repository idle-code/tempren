from pathlib import Path
from typing import Optional

import pytest
from pint import UndefinedUnitError

from tempren.exceptions import ExpressionEvaluationError
from tempren.primitives import File
from tempren.tags.core import (
    AsDistanceTag,
    AsDurationTag,
    AsIntTag,
    AsSizeTag,
    AsTimeTag,
    BaseTag,
    CountTag,
    DefaultTag,
    DirTag,
    EvalTag,
    ExtTag,
    IsMimeTag,
    MimeExtTag,
    MimeTag,
    NameTag,
    RoundTag,
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


class TestIsMimeTag:
    def test_text_type(self, text_data_dir: Path):
        tag = IsMimeTag()
        tag.configure("text")
        file = File(text_data_dir, Path("hello.txt"))

        is_text = tag.process(file, None)

        assert is_text

    def test_not_text_type(self, audio_data_dir: Path):
        tag = IsMimeTag()
        tag.configure("text")
        file = File(audio_data_dir, Path("sample.mp3"))

        is_text = tag.process(file, None)

        assert not is_text

    def test_audio_type(self, audio_data_dir: Path):
        tag = IsMimeTag()
        tag.configure("audio")
        file = File(audio_data_dir, Path("sample.flac"))

        is_audio = tag.process(file, None)

        assert is_audio

    def test_audio_type_full_match(self, audio_data_dir: Path):
        tag = IsMimeTag()
        tag.configure("audio/flac")
        file = File(audio_data_dir, Path("sample.flac"))

        is_flac = tag.process(file, None)

        assert is_flac


class TestDefaultTag:
    def test_no_default_value_provided(self):
        tag = DefaultTag()

        with pytest.raises(TypeError):
            tag.configure()

    def test_non_empty_context(self, nonexistent_file: File):
        tag = DefaultTag()
        tag.configure("default")

        result = tag.process(nonexistent_file, "value")

        assert result == "value"

    def test_empty_context(self, nonexistent_file: File):
        tag = DefaultTag()
        tag.configure("default")

        result = tag.process(nonexistent_file, "")

        assert result == "default"

    def test_whitespace_context(self, nonexistent_file: File):
        tag = DefaultTag()
        tag.configure("default")

        result = tag.process(nonexistent_file, "  \t")

        assert result == "default"


class TestAsSizeTag:
    def test_no_unit(self):
        tag = AsSizeTag()

        with pytest.raises(ValueError):
            tag.configure(None)

    def test_unknown_unit(self):
        tag = AsSizeTag()

        with pytest.raises(ValueError):
            tag.configure("spam")

    def test_invalid_precision(self):
        tag = AsSizeTag()

        with pytest.raises(ValueError):
            tag.configure("KiB", -2)

    @pytest.mark.parametrize("unit", ("k", "K", "kb", "KB", "kib", "KiB"))
    def test_unit_case(self, nonexistent_file: File, unit: str):
        tag = AsSizeTag()
        tag.configure(unit)

        size_in_unit = tag.process(nonexistent_file, "1024")

        assert size_in_unit == "1"

    @pytest.mark.parametrize(
        "unit,unit_multiplier",
        [
            ("k", 1024),
            ("kB", 1024),
            ("KiB", 1024),
            ("M", 1024**2),
            ("MB", 1024**2),
            ("MiB", 1024**2),
            ("G", 1024**3),
            ("GB", 1024**3),
            ("GiB", 1024**3),
            ("TB", 1024**4),
            ("T", 1024**4),
            ("TiB", 1024**4),
            ("P", 1024**5),
            ("PB", 1024**5),
            ("PiB", 1024**5),
        ],
    )
    @pytest.mark.parametrize(
        "precision,size_multiplier,expected_output",
        [
            (None, 0.5, "0"),
            (None, 1, "1"),
            (None, 1.5, "2"),
            (None, 12.34, "12"),
            (1, 0.5, "0.5"),
            (1, 1, "1.0"),
            (1, 1.5, "1.5"),
            (2, 12.34, "12.34"),
        ],
    )
    def test_unit_rounding(
        self,
        nonexistent_file: File,
        unit: str,
        unit_multiplier: float,
        precision: Optional[int],
        size_multiplier: float,
        expected_output: str,
    ):
        tag = AsSizeTag()
        tag.configure(unit, precision)
        size_in_bytes = size_multiplier * unit_multiplier

        size_in_unit = tag.process(nonexistent_file, str(size_in_bytes))

        assert size_in_unit == expected_output


class TestRoundTag:
    def test_no_precision_specified(self, nonexistent_file: File):
        tag = RoundTag()
        tag.configure()

        rounded = tag.process(nonexistent_file, "123.456")

        assert rounded == "123"

    def test_zero_precision(self, nonexistent_file: File):
        tag = RoundTag()
        tag.configure(0)

        rounded = tag.process(nonexistent_file, "123.456")

        assert rounded == "123"

    def test_positive_precision(self, nonexistent_file: File):
        tag = RoundTag()
        tag.configure(2)

        rounded = tag.process(nonexistent_file, "123.456")

        assert rounded == "123.46"

    def test_negative_precision(self, nonexistent_file: File):
        tag = RoundTag()
        tag.configure(-2)

        rounded = tag.process(nonexistent_file, "123.456")

        assert rounded == "100"

    def test_precision_and_up_down_rounding(self):
        tag = RoundTag()

        with pytest.raises(ValueError):
            tag.configure(2, down=True)

    def test_up_and_down_rounding(self):
        tag = RoundTag()

        with pytest.raises(ValueError):
            tag.configure(down=True, up=True)

    def test_ceil_rounding(self, nonexistent_file: File):
        tag = RoundTag()
        tag.configure(up=True)

        rounded = tag.process(nonexistent_file, "123.456")

        assert rounded == "124"

    def test_floor_rounding(self, nonexistent_file: File):
        tag = RoundTag()
        tag.configure(down=True)

        rounded = tag.process(nonexistent_file, "123.456")

        assert rounded == "123"


class TestEvalTag:
    def test_empty_context(self, nonexistent_file: File):
        tag = EvalTag()
        tag.configure()

        with pytest.raises(ExpressionEvaluationError):
            tag.process(nonexistent_file, "")

    def test_numeric_expression(self, nonexistent_file: File):
        tag = EvalTag()
        tag.configure()

        result = tag.process(nonexistent_file, "2 + 3")

        assert result == 5


class TestAsTimeTag:
    def test_invalid_input(self, nonexistent_file: File):
        tag = AsTimeTag()
        tag.configure("%d-%m-%y")

        with pytest.raises(ValueError):
            tag.process(nonexistent_file, "foobar")

    def test_valid_format(self, nonexistent_file: File):
        tag = AsTimeTag()
        tag.configure("%d-%m-%y")

        result = tag.process(nonexistent_file, "2020-10-15T11:33:39")

        assert result == "15-10-20"


class TestAsDurationTag:
    def test_invalid_input(self, nonexistent_file: File):
        tag = AsDurationTag()
        tag.configure("%h%m%s")

        with pytest.raises(ValueError):
            tag.process(nonexistent_file, "foobar")

    def test_valid_format(self, nonexistent_file: File):
        tag = AsDurationTag()
        tag.configure("%S-%M-%H-%d-%m-%Y")

        result = tag.process(nonexistent_file, "P1Y2M3DT4H5M6S")

        assert result == "06-05-04-03-02-0001"


class TestAsIntTag:
    def test_invalid_input(self, nonexistent_file: File):
        tag = AsIntTag()
        tag.configure()

        with pytest.raises(ValueError):
            tag.process(nonexistent_file, "foobar")

    def test_invalid_source_base(self):
        tag = AsIntTag()

        with pytest.raises(ValueError):
            tag.configure(src_base=13)

    def test_invalid_destination_base(self):
        tag = AsIntTag()

        with pytest.raises(ValueError):
            tag.configure(dst_base=13)

    def test_positive_number(self, nonexistent_file: File):
        tag = AsIntTag()
        tag.configure()

        number = tag.process(nonexistent_file, "10")

        assert number == "10"

    def test_remove_leading_zeros(self, nonexistent_file: File):
        tag = AsIntTag()
        tag.configure()

        number = tag.process(nonexistent_file, "023")

        assert number == "23"

    def test_hex_to_dec(self, nonexistent_file: File):
        tag = AsIntTag()
        tag.configure(16, 10)

        number = tag.process(nonexistent_file, "BEEF")

        assert number == "48879"

    def test_oct_to_bin(self, nonexistent_file: File):
        tag = AsIntTag()
        tag.configure(8, 2)

        number = tag.process(nonexistent_file, "776")

        assert number == "111111110"


@pytest.mark.slow  # TODO: Store UnitRegistry at module level to improve startup time this tag
class TestAsDistanceTag:
    def test_invalid_target_unit(self):
        tag = AsDistanceTag()

        with pytest.raises(UndefinedUnitError):
            tag.configure("foobar")

    def test_invalid_source_unit(self):
        tag = AsDistanceTag()

        with pytest.raises(UndefinedUnitError):
            tag.configure("km", "foobar")

    def test_invalid_input(self, nonexistent_file: File):
        tag = AsDistanceTag()
        tag.configure("km")

        with pytest.raises(ValueError):
            tag.process(nonexistent_file, "foobar")

    def test_meters_to_foot(self, nonexistent_file: File):
        tag = AsDistanceTag()
        tag.configure("ft")

        result = tag.process(nonexistent_file, "1")

        assert abs(result - 3.28) < 0.01

    def test_miles_to_kilometers(self, nonexistent_file: File):
        tag = AsDistanceTag()
        tag.configure("km", "mile")

        result = tag.process(nonexistent_file, "10")

        assert abs(result - 16.09) < 0.01
