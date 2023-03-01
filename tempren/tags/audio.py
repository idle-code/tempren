from abc import ABC
from datetime import timedelta
from typing import Any, Dict, Optional

import mutagen
import mutagen.mp3
from mutagen.easyid3 import EasyID3

from tempren.exceptions import MissingMetadataError
from tempren.primitives import File, Tag


class MutagenTagBase(Tag, ABC):
    """Extracts audio metadata (tags) using mutagen library"""

    require_context = False

    tag_key: str

    def process(self, file: File, context: Optional[str]) -> Any:
        metadata_dict = self._extract_metadata(file)
        if self.tag_key not in metadata_dict:
            raise MissingMetadataError()
        tag_value = self.format_value(metadata_dict[self.tag_key])
        if isinstance(tag_value, list):
            tag_value = "\n".join(tag_value)
        return tag_value

    def _extract_metadata(self, file: File) -> Dict[str, Any]:
        # TODO: Check if File(..., easy=True) could improve readability here
        audio_file = mutagen.File(file.absolute_path)
        metadata_dict = dict()
        metadata_dict["duration"] = audio_file.info.length
        metadata_dict["channels"] = audio_file.info.channels
        metadata_dict["sample_rate"] = audio_file.info.sample_rate
        metadata_dict["bitrate"] = audio_file.info.bitrate
        if isinstance(audio_file, mutagen.mp3.MP3):
            metadata_dict["comments"] = audio_file.get("COMM::XXX", "")
            audio_file = mutagen.mp3.MP3(file.absolute_path, ID3=EasyID3)
        else:
            metadata_dict["bits_per_sample"] = audio_file.info.bits_per_sample

        metadata_dict.update(dict(audio_file))
        return metadata_dict

    def format_value(self, metadata_value: Any):
        return metadata_value


class TitleTag(MutagenTagBase):
    """Track title"""

    tag_key = "title"


class AlbumTag(MutagenTagBase):
    """Album name"""

    tag_key = "album"


class ArtistTag(MutagenTagBase):
    """Name of the artist"""

    tag_key = "artist"


class CommentTag(MutagenTagBase):
    """Comment"""

    tag_key = "comments"


class YearTag(MutagenTagBase):
    """Year of the release"""

    tag_key = "date"


class GenreTag(MutagenTagBase):
    """Genre type"""

    tag_key = "genre"


class TrackTag(MutagenTagBase):
    """Track number"""

    tag_key = "tracknumber"


class DurationTag(MutagenTagBase):
    """Track duration in seconds"""

    tag_key = "duration"

    def format_value(self, metadata_value: Any):
        duration_in_seconds = float(super().format_value(metadata_value))
        return timedelta(seconds=duration_in_seconds)


class ChannelsTag(MutagenTagBase):
    """Number of channels"""

    tag_key = "channels"


class SampleRateTag(MutagenTagBase):
    """Sample rate"""

    tag_key = "sample_rate"


class BitRateTag(MutagenTagBase):
    """Bit rate"""

    tag_key = "bitrate"


class BitsPerSampleTag(MutagenTagBase):
    """Bit rate per sample"""

    tag_key = "bits_per_sample"
