from datetime import timedelta
from pathlib import Path

import pytest

from tempren.exceptions import FileNotSupportedError, MissingMetadataError
from tempren.primitives import File, Tag
from tempren.tags.video import (
    AspectRatioTag,
    BitRateTag,
    DurationTag,
    FrameCountTag,
    FrameRateTag,
    HeightTag,
    VideoCodecTag,
    WidthTag,
)


# noinspection PyMethodMayBeStatic
class VideoInfoTagTests:
    def test_invalid_file_type(self, tag: Tag, text_data_dir: Path):
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)

    def test_missing_video_track(self, tag: Tag, audio_data_dir: Path):
        sample_file = File(audio_data_dir, Path("sample.mp3"))

        with pytest.raises(MissingMetadataError):
            tag.process(sample_file, None)


class TestWidthTag(VideoInfoTagTests):
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


class TestHeightTag(VideoInfoTagTests):
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


class TestAspectRatioTag(VideoInfoTagTests):
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


class TestFrameRateTag(VideoInfoTagTests):
    @pytest.fixture
    def tag(self):
        return FrameRateTag()

    def test_frame_rate(self, tag: FrameRateTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        frame_rate = tag.process(video_file, None)

        assert abs(frame_rate - 5) < 0.01


class TestFrameCountTag(VideoInfoTagTests):
    @pytest.fixture
    def tag(self):
        return FrameCountTag()

    def test_frame_count(self, tag: FrameCountTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        frame_count = tag.process(video_file, None)

        assert frame_count == 14


class TestVideoCodecTag(VideoInfoTagTests):
    @pytest.fixture
    def tag(self):
        return VideoCodecTag()

    def test_mp4_codec(self, tag: VideoCodecTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        video_codec = tag.process(video_file, None)

        assert video_codec == "AVC"

    def test_mkv_codec(self, tag: VideoCodecTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mkv"))

        video_codec = tag.process(video_file, None)

        assert video_codec == "VP9"


class TestDurationTag(VideoInfoTagTests):
    @pytest.fixture
    def tag(self):
        return DurationTag()

    def test_duration(self, tag: DurationTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        duration = tag.process(video_file, None)

        assert duration == timedelta(seconds=2, milliseconds=800)


class TestBitRateTag(VideoInfoTagTests):
    @pytest.fixture
    def tag(self):
        return BitRateTag()

    def test_mp4_bit_rate(self, tag: VideoCodecTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mp4"))

        bit_rate = tag.process(video_file, None)

        assert bit_rate == 1329477

    def test_mkv_bit_rate(self, tag: VideoCodecTag, video_data_dir: Path):
        video_file = File(video_data_dir, Path("timelapse.mkv"))

        bit_rate = tag.process(video_file, None)

        assert bit_rate == 473503
