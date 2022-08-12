from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.video import (
    AspectRatioTag,
    FrameCountTag,
    FrameRateTag,
    HeightTag,
    WidthTag,
)
from tempren.template.tree_elements import FileNotSupportedError, Tag


class MediaInfoTagTests:
    def test_invalid_file_type(self, tag: Tag, text_data_dir: Path):
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestWidthTag(MediaInfoTagTests):
    @pytest.fixture
    def tag(self) -> WidthTag:
        return WidthTag()

    def test_mp4_width(self, tag: WidthTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        width = tag.process(video_file, None)

        assert width == 800

    def test_mkv_width(self, tag: WidthTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mkv"))

        width = tag.process(video_file, None)

        assert width == 600


class TestHeightTag(MediaInfoTagTests):
    @pytest.fixture
    def tag(self) -> HeightTag:
        return HeightTag()

    def test_mp4_height(self, tag: HeightTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        height = tag.process(video_file, None)

        assert height == 600

    def test_mkv_height(self, tag: HeightTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mkv"))

        height = tag.process(video_file, None)

        assert height == 450


class TestAspectRatioTag(MediaInfoTagTests):
    @pytest.fixture
    def tag(self):
        return AspectRatioTag()

    def test_4_to_3_fraction(self, tag: AspectRatioTag, video_data_dir: Path):
        tag.configure()
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        ratio = tag.process(video_file, None)

        assert ratio == "4:3"

    def test_4_to_3_decimal(self, tag: AspectRatioTag, video_data_dir: Path):
        tag.configure(decimal=True)
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        ratio = tag.process(video_file, None)

        assert abs(ratio - 1.33) < 0.01


class TestFrameRateTag(MediaInfoTagTests):
    @pytest.fixture
    def tag(self):
        return FrameRateTag()

    def test_frame_rate(self, tag: FrameRateTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        frame_rate = tag.process(video_file, None)

        assert abs(frame_rate - 5) < 0.01


class TestFrameCountTag(MediaInfoTagTests):
    @pytest.fixture
    def tag(self):
        return FrameCountTag()

    def test_frame_count(self, tag: FrameCountTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        frame_count = tag.process(video_file, None)

        assert frame_count == 14
