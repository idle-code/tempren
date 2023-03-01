from abc import ABC, abstractmethod
from datetime import timedelta
from fractions import Fraction
from typing import Any, Optional

from pymediainfo import MediaInfo

from tempren.exceptions import FileNotSupportedError, MissingMetadataError
from tempren.primitives import File, Tag

if not MediaInfo.can_parse():
    raise NotImplementedError("MediaInfo library not found")


class MediaInfoTagBase(Tag, ABC):
    require_context = False

    def process(self, file: File, context: Optional[str]) -> Any:
        media_info = MediaInfo.parse(file.absolute_path)
        if len(media_info.tracks) < 2:  # General track seems always present
            raise FileNotSupportedError()
        return self.extract_metadata(media_info)

    @abstractmethod
    def extract_metadata(self, media_info: MediaInfo) -> Any:
        raise NotImplementedError()


class VideoInfoTagBase(MediaInfoTagBase, ABC):
    def extract_metadata(self, media_info: MediaInfo) -> Any:
        if not media_info.video_tracks:
            raise MissingMetadataError()
        return self.extract_video_metadata(media_info.video_tracks[0])

    @abstractmethod
    def extract_video_metadata(self, video_track) -> Any:
        raise NotImplementedError()


class WidthTag(VideoInfoTagBase):
    """Video width in pixels"""

    def extract_video_metadata(self, video_track) -> Any:
        return video_track.width


class HeightTag(VideoInfoTagBase):
    """Video height in pixels"""

    def extract_video_metadata(self, video_track) -> Any:
        return video_track.height


class AspectRatioTag(VideoInfoTagBase):
    """Video aspect ratio (in fractional W:H or decimal format)"""

    use_decimal: bool

    def configure(self, decimal: bool = False):
        """
        :param decimal: use decimal notation
        """
        self.use_decimal = decimal

    def extract_video_metadata(self, video_track) -> Any:
        if self.use_decimal:
            return video_track.width / video_track.height
        else:
            aspect_ratio = Fraction(video_track.width, video_track.height)
            return f"{aspect_ratio.numerator}:{aspect_ratio.denominator}"


class FrameRateTag(VideoInfoTagBase):
    """Decimal frame rate per second"""

    def extract_video_metadata(self, video_track) -> Any:
        return float(video_track.frame_rate)


class VideoCodecTag(VideoInfoTagBase):
    """Name of video encoding codec"""

    def extract_video_metadata(self, video_track) -> Any:
        return video_track.format


class FrameCountTag(VideoInfoTagBase):
    """Number of frames in the file"""

    def extract_video_metadata(self, video_track) -> Any:
        return int(video_track.frame_count)


class DurationTag(VideoInfoTagBase):
    """Video duration in seconds"""

    def extract_video_metadata(self, video_track) -> timedelta:
        return timedelta(milliseconds=video_track.duration)


class BitRateTag(VideoInfoTagBase):
    """Video stream bit rate"""

    def extract_video_metadata(self, video_track) -> int:
        return int(video_track.bit_rate)
