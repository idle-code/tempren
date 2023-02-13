from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.gpx import ActivityTag, DurationTag, EndTimeTag, StartTimeTag
from tempren.template.tree_elements import FileNotSupportedError, Tag


# noinspection PyMethodMayBeStatic
class GpxTagTests:
    def test_invalid_file_content(self, tag: Tag, text_data_dir: Path):
        text_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)

    def test_invalid_file_type(self, tag: Tag, image_data_dir: Path):
        text_file = File(image_data_dir, Path("park.png"))

        with pytest.raises(FileNotSupportedError):
            tag.process(text_file, None)


class TestStartTimeTag(GpxTagTests):
    @pytest.fixture
    def tag(self) -> StartTimeTag:
        return StartTimeTag()

    def test_activity_start_time(self, tag: StartTimeTag, gpx_data_dir: Path):
        walk_file = File(gpx_data_dir, Path("walk.gpx"))

        result = tag.process(walk_file, None)

        assert result == datetime(
            2022, 8, 3, 7, 28, 58, 552000, tzinfo=timezone(timedelta(hours=2))
        )


class TestEndTimeTag(GpxTagTests):
    @pytest.fixture
    def tag(self) -> EndTimeTag:
        return EndTimeTag()

    def test_activity_end_time(self, tag: EndTimeTag, gpx_data_dir: Path):
        walk_file = File(gpx_data_dir, Path("walk.gpx"))

        result = tag.process(walk_file, None)

        assert result == datetime(
            2022, 8, 3, 7, 55, 40, 826000, tzinfo=timezone(timedelta(hours=2))
        )


class TestActivityTagTag(GpxTagTests):
    @pytest.fixture
    def tag(self) -> ActivityTag:
        return ActivityTag()

    def test_activity_type(self, tag: ActivityTag, gpx_data_dir: Path):
        walk_file = File(gpx_data_dir, Path("walk.gpx"))

        result = tag.process(walk_file, None)

        assert result == "spacer"


class TestDurationTagTag(GpxTagTests):
    @pytest.fixture
    def tag(self) -> DurationTag:
        return DurationTag()

    def test_duration(self, tag: DurationTag, gpx_data_dir: Path):
        walk_file = File(gpx_data_dir, Path("walk.gpx"))

        result = tag.process(walk_file, None)

        assert result == timedelta(minutes=26, seconds=42, microseconds=274000)
