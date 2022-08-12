from abc import ABC, abstractmethod
from fractions import Fraction
from typing import Any, Optional

from pymediainfo import MediaInfo

from tempren.path_generator import File
from tempren.template.tree_elements import FileNotSupportedError, Tag

if not MediaInfo.can_parse():
    raise NotImplementedError("MediaInfo library not found")


class MediaInfoTagBase(Tag, ABC):
    require_context = False

    def process(self, file: File, context: Optional[str]) -> Any:
        media_info = MediaInfo.parse(file.absolute_path)
        if not media_info.video_tracks:
            raise FileNotSupportedError()
        return self.extract_metadata(media_info)

    @abstractmethod
    def extract_metadata(self, media_info: MediaInfo) -> Any:
        raise NotImplementedError()


class WidthTag(MediaInfoTagBase):
    """Video width in pixels"""

    def extract_metadata(self, media_info: MediaInfo) -> Any:
        video_track = media_info.video_tracks[0]
        return video_track.width


class HeightTag(MediaInfoTagBase):
    """Video height in pixels"""

    def extract_metadata(self, media_info: MediaInfo) -> Any:
        video_track = media_info.video_tracks[0]
        return video_track.height


class AspectRatioTag(MediaInfoTagBase):
    """Video aspect ratio (in fractional W:H or decimal format)"""

    use_decimal: bool

    def configure(self, decimal: bool = False):
        """
        :param decimal: use decimal notation
        """
        self.use_decimal = decimal

    def extract_metadata(self, media_info: MediaInfo) -> Any:
        video_track = media_info.video_tracks[0]
        if self.use_decimal:
            return video_track.width / video_track.height
        else:
            aspect_ratio = Fraction(video_track.width, video_track.height)
            return f"{aspect_ratio.numerator}:{aspect_ratio.denominator}"


class FrameRateTag(MediaInfoTagBase):
    """Decimal frame rate per second"""

    def extract_metadata(self, media_info: MediaInfo) -> float:
        video_track = media_info.video_tracks[0]
        return float(video_track.frame_rate)


class FrameCountTag(MediaInfoTagBase):
    """Number of frames in file"""

    def extract_metadata(self, media_info: MediaInfo) -> int:
        video_track = media_info.video_tracks[0]
        return int(video_track.frame_count)
