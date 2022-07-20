from abc import ABC
from typing import Any, Dict, List, Optional

import mutagen
import mutagen.mp3
from mutagen.easyid3 import EasyID3

from tempren.path_generator import File
from tempren.template.tree_elements import MissingMetadataError, Tag


class MutagenTag(Tag, ABC):
    """Extract audio metadata (tags) using mutagen library"""

    require_context = False

    tag_key: str

    def process(self, file: File, context: Optional[str]) -> Any:
        metadata_dict = self._extract_metadata(file)
        if self.tag_key not in metadata_dict:
            raise MissingMetadataError()
        tag_value = metadata_dict[self.tag_key]
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
            metadata_dict["comments"] = audio_file["COMM::XXX"]
            audio_file = mutagen.mp3.MP3(file.absolute_path, ID3=EasyID3)
        else:
            metadata_dict["bits_per_sample"] = audio_file.info.bits_per_sample

        metadata_dict.update(dict(audio_file))
        return metadata_dict


class TitleTag(MutagenTag):
    """Extract track title"""

    tag_key = "title"


class AlbumTag(MutagenTag):
    """Extract album name"""

    tag_key = "album"


class ArtistTag(MutagenTag):
    """Extract name of the artist"""

    tag_key = "artist"


class CommentTag(MutagenTag):
    """Extract comment"""

    tag_key = "comments"


class YearTag(MutagenTag):
    """Extract year of the release"""

    tag_key = "date"


class GenreTag(MutagenTag):
    """Extract genre type"""

    tag_key = "genre"


class TrackTag(MutagenTag):
    """Extract track number"""

    tag_key = "tracknumber"


class DurationTag(MutagenTag):
    """Extract track duration in seconds"""

    tag_key = "duration"


class ChannelsTag(MutagenTag):
    """Extract number of channels"""

    tag_key = "channels"


class SampleRateTag(MutagenTag):
    """Extract sample rate"""

    tag_key = "sample_rate"


class BitRateTag(MutagenTag):
    """Extract bit rate"""

    tag_key = "bitrate"


class BitsPerSampleTag(MutagenTag):
    """Extract bit rate"""

    tag_key = "bits_per_sample"
