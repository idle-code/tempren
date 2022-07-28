from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.image import (
    AspectRatioTag,
    ColorModeTag,
    ExifTag,
    FormatTag,
    HeightTag,
    WidthTag,
)
from tempren.template.tree_elements import FileNotSupportedError, MissingMetadataError


class TestWidthTag:
    def test_jpg_width(self, image_data_dir: Path):
        tag = WidthTag()
        image_file = File(image_data_dir, Path("photo.jpg"))

        width = tag.process(image_file, None)

        assert width == 1008

    def test_png_width(self, image_data_dir: Path):
        tag = WidthTag()
        image_file = File(image_data_dir, Path("park.png"))

        width = tag.process(image_file, None)

        assert width == 480

    def test_invalid_file_type(self, text_data_dir: Path):
        tag = WidthTag()
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestHeightTag:
    def test_jpg_height(self, image_data_dir: Path):
        tag = HeightTag()
        image_file = File(image_data_dir, Path("photo.jpg"))

        height = tag.process(image_file, None)

        assert height == 567

    def test_png_height(self, image_data_dir: Path):
        tag = HeightTag()
        image_file = File(image_data_dir, Path("park.png"))

        height = tag.process(image_file, None)

        assert height == 480

    def test_invalid_file_type(self, text_data_dir: Path):
        tag = HeightTag()
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestFormatTag:
    def test_jpg_format(self, image_data_dir: Path):
        tag = FormatTag()
        image_file = File(image_data_dir, Path("photo.jpg"))

        image_format = tag.process(image_file, None)

        assert image_format == "JPEG"

    def test_png_format(self, image_data_dir: Path):
        tag = FormatTag()
        image_file = File(image_data_dir, Path("park.png"))

        image_format = tag.process(image_file, None)

        assert image_format == "PNG"

    def test_invalid_file_type(self, text_data_dir: Path):
        tag = FormatTag()
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestModeTag:
    def test_rgb_mode(self, image_data_dir: Path):
        tag = ColorModeTag()
        image_file = File(image_data_dir, Path("photo.jpg"))

        image_mode = tag.process(image_file, None)

        assert image_mode == "RGB"

    def test_rgba_format(self, image_data_dir: Path):
        tag = ColorModeTag()
        image_file = File(image_data_dir, Path("park.png"))

        image_mode = tag.process(image_file, None)

        assert image_mode == "RGBA"

    def test_invalid_file_type(self, text_data_dir: Path):
        tag = ColorModeTag()
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestAspectRatioTag:
    def test_16_to_9_fraction(self, image_data_dir: Path):
        tag = AspectRatioTag()
        tag.configure()
        image_file = File(image_data_dir, Path("photo.jpg"))

        ratio = tag.process(image_file, None)

        assert ratio == "16:9"

    def test_1_to_1_fraction(self, image_data_dir: Path):
        tag = AspectRatioTag()
        tag.configure()
        image_file = File(image_data_dir, Path("park.png"))

        ratio = tag.process(image_file, None)

        assert ratio == "1:1"

    def test_16_to_9_decimal(self, image_data_dir: Path):
        tag = AspectRatioTag()
        tag.configure(decimal=True)
        image_file = File(image_data_dir, Path("photo.jpg"))

        ratio = tag.process(image_file, None)

        assert abs(ratio - 1.77) < 0.01

    def test_1_to_1_decimal(self, image_data_dir: Path):
        tag = AspectRatioTag()
        tag.configure(decimal=True)
        image_file = File(image_data_dir, Path("park.png"))

        ratio = tag.process(image_file, None)

        assert abs(ratio - 1.0) < 0.01

    def test_invalid_file_type(self, text_data_dir: Path):
        tag = AspectRatioTag()
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestExifTag:
    def test_no_tag_name_provided(self, image_data_dir: Path):
        tag = ExifTag()

        with pytest.raises(AssertionError):
            tag.configure("")

    def test_unknown_tag_name(self, image_data_dir: Path):
        tag = ExifTag()

        with pytest.raises(ValueError):
            tag.configure("Unknown tag name")

    def test_missing_tag_value(self, image_data_dir: Path):
        tag = ExifTag()
        tag.configure("BitsPerSample")
        image_file = File(image_data_dir, Path("photo.jpg"))

        with pytest.raises(MissingMetadataError):
            tag.process(image_file, None)

    def test_date_time(self, image_data_dir: Path):
        tag = ExifTag()
        tag.configure("DateTime")
        image_file = File(image_data_dir, Path("photo.jpg"))

        gps_date_stamp = tag.process(image_file, None)

        assert gps_date_stamp == "2019:02:17 07:20:40"

    def test_gps_date_stamp_ascii(self, image_data_dir: Path):
        tag = ExifTag()
        tag.configure("GPSDateStamp")
        image_file = File(image_data_dir, Path("photo.jpg"))

        gps_date_stamp = tag.process(image_file, None)

        assert gps_date_stamp == "2019:02:17"

    def test_focal_length_rational(self, image_data_dir: Path):
        tag = ExifTag()
        tag.configure("FocalLength")
        image_file = File(image_data_dir, Path("photo.jpg"))

        focal_length = tag.process(image_file, None)

        assert abs(focal_length - 4.2) < 0.01

    def test_focal_length_mm_short(self, image_data_dir: Path):
        tag = ExifTag()
        tag.configure("FocalLengthIn35mmFilm")
        image_file = File(image_data_dir, Path("photo.jpg"))

        focal_length_mm = tag.process(image_file, None)

        assert focal_length_mm == 26
