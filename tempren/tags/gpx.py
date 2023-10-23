from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional

import gpxpy
from gpxpy.gpx import GPX, GPXXMLSyntaxException

from tempren.exceptions import FileNotSupportedError, MissingMetadataError
from tempren.primitives import File, Tag


class GpxTagBase(Tag, ABC):
    require_context = False

    def process(self, file: File, context: Optional[str]) -> Any:
        try:
            with open(file.absolute_path, "r") as gpx_file:
                parsed_gpx = gpxpy.parse(gpx_file)
                return self.extract_metadata(parsed_gpx)
        except (GPXXMLSyntaxException, UnicodeDecodeError):
            raise FileNotSupportedError()

    @abstractmethod
    def extract_metadata(self, gpx: GPX) -> Any:
        raise NotImplementedError()


class StartTimeTag(GpxTagBase):
    """Start time of the first segment in the file (in ISO 8601 format)"""

    def extract_metadata(self, gpx: GPX) -> Any:
        time_bounds = gpx.get_time_bounds()
        if not time_bounds.start_time:
            raise MissingMetadataError()
        return time_bounds.start_time


class EndTimeTag(GpxTagBase):
    """End time of the last segment in the file (in ISO 8601 format)"""

    def extract_metadata(self, gpx: GPX) -> Any:
        time_bounds = gpx.get_time_bounds()
        if not time_bounds.end_time:
            raise MissingMetadataError()
        return time_bounds.end_time


class ActivityTag(GpxTagBase):
    """Type of the activity"""

    def extract_metadata(self, gpx: GPX) -> Any:
        if not gpx.tracks:
            raise MissingMetadataError()
        track = gpx.tracks[0]
        return track.type


class DurationTag(GpxTagBase):
    """Duration of the activity"""

    def extract_metadata(self, gpx: GPX) -> timedelta:
        duration_seconds = gpx.get_duration()
        if not duration_seconds:
            raise MissingMetadataError()
        return timedelta(seconds=duration_seconds)


class DistanceTag(GpxTagBase):
    """Total distance travelled (in meters)"""

    def extract_metadata(self, gpx: GPX) -> float:
        distance_meters = gpx.length_3d()
        gpx.get_elevation_extremes()
        if distance_meters == 0:
            raise MissingMetadataError()
        return distance_meters


class ElevationChangeTag(GpxTagBase):
    """Maximum elevation change (in meters)"""

    def extract_metadata(self, gpx: GPX) -> float:
        extremes = gpx.get_elevation_extremes()
        if not extremes.minimum or not extremes.maximum:
            raise MissingMetadataError()
        return extremes.maximum - extremes.minimum


class AverageSpeedTag(GpxTagBase):
    """Average speed (in meters/second)"""

    def extract_metadata(self, gpx: GPX) -> float:
        moving_data = gpx.get_moving_data()
        if moving_data.moving_distance == 0 or moving_data.moving_time == 0:
            raise MissingMetadataError()
        return moving_data.moving_distance / moving_data.moving_time
