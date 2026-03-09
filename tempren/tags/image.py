import itertools
from abc import ABC, abstractmethod
from collections.abc import Iterator
from fractions import Fraction
from typing import Any

import PIL
import PIL.ExifTags
from geopy import Point
from PIL.ExifTags import IFD
from PIL.Image import Image
from PIL.TiffImagePlugin import IFDRational

from tempren.alias import TagAlias
from tempren.exceptions import FileNotSupportedError, MissingMetadataError
from tempren.primitives import File, Tag


class PillowTagBase(Tag, ABC):
    """Base for tags extracting metadata from images using Pillow library"""

    require_context = False

    def process(self, file: File, context: str | None) -> Any:
        try:
            with PIL.Image.open(file.absolute_path) as img:
                return self.extract_metadata(img)
        except (PIL.UnidentifiedImageError, SystemError):
            raise FileNotSupportedError()

    @abstractmethod
    def extract_metadata(self, image: Image) -> Any:
        raise NotImplementedError()


class WidthTag(PillowTagBase):
    """Image width in pixels"""

    def extract_metadata(self, image: Image) -> Any:
        return image.width


class HeightTag(PillowTagBase):
    """Image height in pixels"""

    def extract_metadata(self, image: Image) -> Any:
        return image.height


class FormatTag(PillowTagBase):
    """Image format ('JPG', 'PNG', ...)"""

    def extract_metadata(self, image: Image) -> Any:
        return image.format


class ColorModeTag(PillowTagBase):
    """Color mode ('RGB', 'RGBA', ...)"""

    def extract_metadata(self, image: Image) -> Any:
        return image.mode


class AspectRatioTag(PillowTagBase):
    """Image aspect ratio (in fractional W:H or decimal format)"""

    use_decimal: bool

    def configure(self, decimal: bool = False):
        """
        :param decimal: use decimal notation
        """
        self.use_decimal = decimal

    def extract_metadata(self, image: Image) -> Any:
        if self.use_decimal:
            return image.width / image.height
        else:
            aspect_ratio = Fraction(image.width, image.height)
            return f"{aspect_ratio.numerator}:{aspect_ratio.denominator}"


class MPxTag(PillowTagBase):
    """Image resolution in megapixels"""

    ndigits: int

    def configure(self, ndigits: int = 2):
        """
        :param ndigits: number of decimal digits
        """
        assert ndigits >= 0, "Precision cannot be negative"
        self.ndigits = ndigits

    def extract_metadata(self, image: Image) -> Any:
        return round(image.width * image.height / 1_000_000, self.ndigits)


class IsOrientationTag(PillowTagBase):
    """Checks image orientation"""

    check_for_landscape: bool
    check_for_portrait: bool

    def configure(self, landscape: bool = False, portrait: bool = False):
        """
        :param landscape: check if image height is greater than width
        :param portrait: check if image width is greater than height
        :returns: True if image have expected orientation
        If both landscape and portrait are specified - check for squareness
        """
        # TODO: check for rotation information in EXIF data?
        assert landscape or portrait, "No orientation specified"
        self.check_for_landscape = landscape
        self.check_for_portrait = portrait

    def extract_metadata(self, image: Image) -> bool:
        if self.check_for_landscape and self.check_for_portrait:
            return image.width == image.height
        if self.check_for_landscape:
            return image.width > image.height
        if self.check_for_portrait:
            return image.width < image.height
        raise NotImplementedError()


# Reverse lookups: tag name -> tag ID
_TAGS_BY_NAME: dict[str, int] = {
    name: tag_id for tag_id, name in PIL.ExifTags.TAGS.items()
}
_GPS_TAGS_BY_NAME: dict[str, int] = {
    name: tag_id for tag_id, name in PIL.ExifTags.GPSTAGS.items()
}


def _validate_tag_name(tag_name: str) -> None:
    """Validate that a tag name is a known EXIF tag."""
    if tag_name not in _TAGS_BY_NAME and tag_name not in _GPS_TAGS_BY_NAME:
        raise ValueError(f"Could not find tag id for '{tag_name}'")


def _convert_exif_value(value: Any) -> Any:
    """Convert Pillow EXIF values to Python-native types."""
    if isinstance(value, IFDRational):
        if value.denominator == 0:
            return 0
        if value.denominator == 1:
            return int(value.numerator)
        return int(value.numerator) / int(value.denominator)
    if isinstance(value, tuple):
        if len(value) == 3 and all(isinstance(v, IFDRational) for v in value):
            degrees, minutes, seconds = (_convert_exif_value(v) for v in value)
            return f"{degrees}°{minutes}′{seconds}″"
        return tuple(_convert_exif_value(v) for v in value)
    return value


def load_exif(file_path: str) -> dict[str, Any]:
    """Load all EXIF data from an image file as a name-keyed dict."""
    with PIL.Image.open(file_path) as img:
        exif = img.getexif()
        if not exif:
            return {}

        result: dict[str, Any] = {}

        # IFD0 (base) tags
        for tag_id, value in exif.items():
            name = PIL.ExifTags.TAGS.get(tag_id)
            if name:
                result[name] = value

        # Exif sub-IFD tags
        for tag_id, value in exif.get_ifd(IFD.Exif).items():
            name = PIL.ExifTags.TAGS.get(tag_id)
            if name:
                result[name] = value

        # GPS sub-IFD tags
        for tag_id, value in exif.get_ifd(IFD.GPSInfo).items():
            name = PIL.ExifTags.GPSTAGS.get(tag_id)
            if name:
                result[name] = value

        return result


def extract_exif_value(exif_data: dict[str, Any], tag_name: str) -> Any:
    """Extract and convert a named EXIF tag value from loaded EXIF data."""
    if tag_name not in exif_data:
        raise MissingMetadataError()
    return _convert_exif_value(exif_data[tag_name])


class ExifTag(Tag):
    """Extract value of any EXIF tag"""

    tag_name: str

    def configure(self, tag_name: str):  # type: ignore
        """
        :param tag_name: name of the tag to extract (e.g. 'FocalLength', 'DateTime', 'FNumber')
        """
        # TODO: generate list of supported tags dynamically
        assert tag_name, "expected non empty tag name"
        # Validate tag name exists (raises ValueError if unknown)
        _validate_tag_name(tag_name)
        self.tag_name = tag_name

    def process(self, file: File, context: str | None) -> Any:
        exif_data = load_exif(str(file.absolute_path))
        return extract_exif_value(exif_data, self.tag_name)


def _generate_exif_tag_list() -> Iterator[str]:
    seen: set[str] = set()
    for tag_name in sorted(
        set(PIL.ExifTags.TAGS.values()) | set(PIL.ExifTags.GPSTAGS.values())
    ):
        if tag_name not in seen:
            seen.add(tag_name)
            yield f"  {tag_name}"


ExifTag.__doc__ = "\n".join(
    itertools.chain(
        [str(ExifTag.__doc__), "Available tag names:"],
        _generate_exif_tag_list(),
    )
)


class ResolutionTagAlias(TagAlias):
    """%Image.Width()x%Image.Height()"""


class GpsPositionTag(Tag):
    """Latitude and longitude of place where photo was taken"""

    require_context = False

    use_decimal: bool

    def configure(self, decimal: bool = True):
        """
        :param decimal: Use simpler decimal notation instead of degrees-minutes-seconds
        """
        self.use_decimal = decimal

    def process(self, file: File, context: str | None) -> Any:
        assert context is None

        exif_data = load_exif(str(file.absolute_path))
        try:
            latitude = extract_exif_value(exif_data, "GPSLatitude")
            latitude_ref = extract_exif_value(exif_data, "GPSLatitudeRef")
            longitude = extract_exif_value(exif_data, "GPSLongitude")
            longitude_ref = extract_exif_value(exif_data, "GPSLongitudeRef")

            degrees_notation = f"{latitude}{latitude_ref}, {longitude}{longitude_ref}"
            if self.use_decimal:
                return Point.from_string(degrees_notation).format_decimal()
            return degrees_notation
        except ValueError:
            return ""


class HasGpsPositionTag(GpsPositionTag):
    """Check if file contains valid GPS coordinates that can be extracted by GpsPosition tag"""

    def process(self, file: File, context: str | None) -> bool:
        # noinspection PyBroadException
        try:
            return super().process(file, context) != ""
        except:
            return False
