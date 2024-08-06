import datetime
from abc import ABC
from datetime import timedelta
from typing import Any, Dict, Optional

import isodate
import mutagen
import mutagen.mp3
from mutagen.easyid3 import EasyID3

from tempren.exceptions import FileNotSupportedError, MissingMetadataError
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
        if audio_file is None:
            raise FileNotSupportedError()
        metadata_dict: Dict[str, Any] = dict()
        self.try_to_extract_property(metadata_dict, audio_file.info, "length")
        self.try_to_extract_property(metadata_dict, audio_file.info, "channels")
        self.try_to_extract_property(metadata_dict, audio_file.info, "sample_rate")
        self.try_to_extract_property(metadata_dict, audio_file.info, "bitrate")
        if isinstance(audio_file, mutagen.mp3.MP3):
            metadata_dict["comments"] = audio_file.get("COMM::XXX", "")
            audio_file = mutagen.mp3.MP3(file.absolute_path, ID3=EasyID3)
        else:
            self.try_to_extract_property(
                metadata_dict, audio_file.info, "bits_per_sample"
            )

        metadata_dict.update(dict(audio_file))
        return metadata_dict

    @staticmethod
    def try_to_extract_property(
        metadata_dict: Dict[str, Any], audio_info, property_name: str
    ):
        if hasattr(audio_info, property_name):
            metadata_dict[property_name] = getattr(audio_info, property_name)

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
    """Track duration in ISO 8601 notation"""

    tag_key = "length"

    def format_value(self, metadata_value: Any):
        duration_seconds = float(super().format_value(metadata_value))
        return isodate.duration_isoformat(timedelta(seconds=duration_seconds))


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
