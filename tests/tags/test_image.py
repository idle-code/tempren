from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.image import (
    AspectRatioTag,
    ColorModeTag,
    ExifTag,
    FormatTag,
    HeightTag,
    MPxTag,
    WidthTag,
)
from tempren.template.tree_elements import (
    FileNotSupportedError,
    MissingMetadataError,
    Tag,
)


class PillowTagTests:
    def test_invalid_file_type(self, tag: Tag, text_data_dir: Path):
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestWidthTag(PillowTagTests):
    @pytest.fixture
    def tag(self):
        return WidthTag()

    def test_jpg_width(self, tag: WidthTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("photo.jpg"))

        width = tag.process(image_file, None)

        assert width == 1008

    def test_png_width(self, tag: WidthTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("park.png"))

        width = tag.process(image_file, None)

        assert width == 480


class TestHeightTag(PillowTagTests):
    @pytest.fixture
    def tag(self):
        return HeightTag()

    def test_jpg_height(self, tag: HeightTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("photo.jpg"))

        height = tag.process(image_file, None)

        assert height == 567

    def test_png_height(self, tag: HeightTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("park.png"))

        height = tag.process(image_file, None)

        assert height == 480


class TestFormatTag(PillowTagTests):
    @pytest.fixture
    def tag(self):
        return FormatTag()

    def test_jpg_format(self, tag: FormatTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("photo.jpg"))

        image_format = tag.process(image_file, None)

        assert image_format == "JPEG"

    def test_png_format(self, tag: FormatTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("park.png"))

        image_format = tag.process(image_file, None)

        assert image_format == "PNG"


class TestModeTag(PillowTagTests):
    @pytest.fixture
    def tag(self):
        return ColorModeTag()

    def test_rgb_mode(self, tag: ColorModeTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("photo.jpg"))

        image_mode = tag.process(image_file, None)

        assert image_mode == "RGB"

    def test_rgba_format(self, tag: ColorModeTag, image_data_dir: Path):
        image_file = File(image_data_dir, Path("park.png"))

        image_mode = tag.process(image_file, None)

        assert image_mode == "RGBA"


class TestAspectRatioTag(PillowTagTests):
    @pytest.fixture
    def tag(self):
        return AspectRatioTag()

    def test_16_to_9_fraction(self, tag: AspectRatioTag, image_data_dir: Path):
        tag.configure()
        image_file = File(image_data_dir, Path("photo.jpg"))

        ratio = tag.process(image_file, None)

        assert ratio == "16:9"

    def test_1_to_1_fraction(self, tag: AspectRatioTag, image_data_dir: Path):
        tag.configure()
        image_file = File(image_data_dir, Path("park.png"))

        ratio = tag.process(image_file, None)

        assert ratio == "1:1"

    def test_16_to_9_decimal(self, tag: AspectRatioTag, image_data_dir: Path):
        tag.configure(decimal=True)
        image_file = File(image_data_dir, Path("photo.jpg"))

        ratio = tag.process(image_file, None)

        assert abs(ratio - 1.77) < 0.01

    def test_1_to_1_decimal(self, tag: AspectRatioTag, image_data_dir: Path):
        tag.configure(decimal=True)
        image_file = File(image_data_dir, Path("park.png"))

        ratio = tag.process(image_file, None)

        assert abs(ratio - 1.0) < 0.01


class TestMPxTag(PillowTagTests):
    @pytest.fixture
    def tag(self):
        return MPxTag()

    def test_invalid_precision(self, tag: MPxTag, image_data_dir: Path):
        with pytest.raises(AssertionError):
            tag.configure(-3)

    def test_zero_precision(self, tag: MPxTag, image_data_dir: Path):
        tag.configure(0)
        image_file = File(image_data_dir, Path("photo.jpg"))

        megapixels = tag.process(image_file, None)

        assert abs(megapixels - 1) < 0.1

    def test_default_precision(self, tag: MPxTag, image_data_dir: Path):
        tag.configure()
        image_file = File(image_data_dir, Path("park.png"))

        megapixels = tag.process(image_file, None)

        assert abs(megapixels - 0.23) < 0.01

    def test_custom_precision(self, tag: MPxTag, image_data_dir: Path):
        tag.configure(4)
        image_file = File(image_data_dir, Path("photo.jpg"))

        megapixels = tag.process(image_file, None)

        assert abs(megapixels - 0.5715) < 0.0001


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
