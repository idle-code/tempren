from datetime import timedelta
from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.tags.audio import (
    AlbumTag,
    ArtistTag,
    BitRateTag,
    BitsPerSampleTag,
    ChannelsTag,
    CommentTag,
    DurationTag,
    GenreTag,
    SampleRateTag,
    TitleTag,
    TrackTag,
    YearTag,
)
from tempren.template.tree_elements import MissingMetadataError


@pytest.mark.parametrize("sample_name", ["sample.flac", "sample.mp3"])
class TestMutagenTags:
    @pytest.fixture
    def sample_file(self, audio_data_dir, sample_name: str) -> File:
        return File(audio_data_dir, Path(sample_name))

    def test_title_extraction(self, sample_file: File):
        tag = TitleTag()

        title = tag.process(sample_file, None)

        assert title == "Sample"

    def test_album_extraction(self, sample_file: File):
        tag = AlbumTag()

        album = tag.process(sample_file, None)

        assert album == "Tempren test data"

    def test_artist_extraction(self, sample_file: File):
        tag = ArtistTag()

        artist = tag.process(sample_file, None)

        assert artist == "Paweł Żukowski"

    def test_comment_extraction(self, sample_file: File):
        tag = CommentTag()

        comment = tag.process(sample_file, None)

        assert comment == "Audio sample to test tag extraction"

    def test_year_extraction(self, sample_file: File):
        tag = YearTag()

        year = tag.process(sample_file, None)

        assert year == "2022"

    def test_genre_extraction(self, sample_file: File):
        tag = GenreTag()

        genre = tag.process(sample_file, None)

        assert genre == "Speech"

    def test_track_extraction(self, sample_file: File):
        tag = TrackTag()

        track = tag.process(sample_file, None)

        assert track == "1"

    def test_duration_extraction(self, sample_file: File):
        tag = DurationTag()

        duration = tag.process(sample_file, None)

        assert duration == timedelta(seconds=1, microseconds=288707)

    def test_channels_extraction(self, sample_file: File):
        tag = ChannelsTag()

        channels = tag.process(sample_file, None)

        assert channels == 2

    def test_sample_rate_extraction(self, sample_file: File):
        tag = SampleRateTag()

        sample_rate = tag.process(sample_file, None)

        assert sample_rate == 44100


@pytest.mark.parametrize("sample_name", ["sample.flac"])
class TestFlacMutagenTags:
    @pytest.fixture
    def sample_file(self, audio_data_dir, sample_name: str) -> File:
        return File(audio_data_dir, Path(sample_name))

    def test_bit_rate_extraction(self, sample_file: File):
        tag = BitRateTag()

        bit_rate = tag.process(sample_file, None)

        assert bit_rate == 640424

    def test_bits_per_sample_extraction(self, sample_file: File):
        tag = BitsPerSampleTag()

        bits_per_sample = tag.process(sample_file, None)

        assert bits_per_sample == 24


@pytest.mark.parametrize("sample_name", ["sample.mp3"])
class TestMp3MutagenTags:
    @pytest.fixture
    def sample_file(self, audio_data_dir, sample_name: str) -> File:
        return File(audio_data_dir, Path(sample_name))

    def test_bit_rate_extraction(self, sample_file: File):
        tag = BitRateTag()

        bit_rate = tag.process(sample_file, None)

        assert bit_rate == 144700

    def test_bits_per_sample_extraction(self, sample_file: File):
        tag = BitsPerSampleTag()

        with pytest.raises(MissingMetadataError):
            tag.process(sample_file, None)
