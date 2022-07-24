from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.image import HeightTag, WidthTag
from tempren.template.tree_elements import FileNotSupportedError, MissingMetadataError


class TestWidthTag:
    def test_jpg_width(self, image_data_dir: Path):
        tag = WidthTag()
        jpeg_file = File(image_data_dir, Path("photo.jpg"))

        width = tag.process(jpeg_file, None)

        assert width == 1008

    def test_png_width(self, image_data_dir: Path):
        tag = WidthTag()
        jpeg_file = File(image_data_dir, Path("park.png"))

        width = tag.process(jpeg_file, None)

        assert width == 480

    def test_invalid_file_type(self, text_data_dir: Path):
        tag = WidthTag()
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestHeightTag:
    def test_jpg_height(self, image_data_dir: Path):
        tag = HeightTag()
        jpeg_file = File(image_data_dir, Path("photo.jpg"))

        height = tag.process(jpeg_file, None)

        assert height == 567

    def test_png_height(self, image_data_dir: Path):
        tag = HeightTag()
        jpeg_file = File(image_data_dir, Path("park.png"))

        height = tag.process(jpeg_file, None)

        assert height == 480

    def test_invalid_file_type(self, text_data_dir: Path):
        tag = HeightTag()
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)
