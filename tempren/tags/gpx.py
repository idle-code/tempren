from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional

import gpxpy
from gpxpy.gpx import GPX, GPXXMLSyntaxException

from tempren.path_generator import File
from tempren.template.tree_elements import (
    FileNotSupportedError,
    MissingMetadataError,
    Tag,
)


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
    """Start time of the first segment in file (in ISO 8601 format)"""

    def extract_metadata(self, gpx: GPX) -> Any:
        time_bounds = gpx.get_time_bounds()
        if not time_bounds.start_time:
            raise MissingMetadataError()
        return time_bounds.start_time


class EndTimeTag(GpxTagBase):
    """End time of the last segment in file (in ISO 8601 format)"""

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
        if not track.type:
            raise MissingMetadataError()
        return track.type


class DurationTag(GpxTagBase):
    """Duration of the activity"""

    def extract_metadata(self, gpx: GPX) -> timedelta:
        duration_seconds = gpx.get_duration()
        if not duration_seconds:
            raise MissingMetadataError()
        return timedelta(seconds=duration_seconds)
