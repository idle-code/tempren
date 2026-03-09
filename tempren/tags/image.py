import itertools
from abc import ABC, abstractmethod
from collections.abc import Iterator
from fractions import Fraction
from typing import Any

import piexif
import PIL
from geopy import Point
from piexif import TAGS
from piexif import TYPES as TAG_TYPES
from PIL.Image import Image

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


def extract_exif_value(exif_dict, tag_name: str):
    tag_id, tag_type = tag_name_to_id_type(tag_name)
    for src in exif_dict.values():
        if isinstance(src, dict) and tag_id in src:
            tag_value = src[tag_id]
            return convert_tag_value(tag_type, tag_value)
    else:
        raise MissingMetadataError()


def tag_name_to_id_type(tag_name: str) -> tuple[int, int]:
    for _, tags in TAGS.items():
        for tag_id, description in tags.items():
            if description["name"] == tag_name:
                return tag_id, description["type"]
    raise ValueError(f"Could not find tag id for '{tag_name}'")


def convert_tag_value(tag_type, tag_value):
    if tag_type in (TAG_TYPES.Rational, TAG_TYPES.SRational):
        if isinstance(tag_value[0], tuple):
            if len(tag_value) == 3:
                # We are probably dealing with GPS coordinates
                (
                    degrees,
                    minutes,
                    seconds,
                ) = (convert_tag_value(tag_type, v) for v in tag_value)
                return f"{degrees}°{minutes}′{seconds}″"
            return " ".join(str(convert_tag_value(tag_type, v)) for v in tag_value)
        else:
            if tag_value[1] == 1:
                return tag_value[0]
            else:
                if tag_value[1] == 0:
                    return 0
                return tag_value[0] / tag_value[1]
    if tag_type == TAG_TYPES.Ascii:
        return tag_value.decode("ascii")
    return tag_value


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
        tag_name_to_id_type(tag_name)
        self.tag_name = tag_name

    def process(self, file: File, context: str | None) -> Any:
        exif_dict = piexif.load(str(file.absolute_path))
        return extract_exif_value(exif_dict, self.tag_name)


_tag_type_map = {
    TAG_TYPES.__dict__[type_name]: type_name
    for type_name in TAG_TYPES.__dict__.keys()
    if isinstance(TAG_TYPES.__dict__[type_name], int)
}


def _generate_exif_tag_list() -> Iterator[str]:
    for _, tags in TAGS.items():
        for tag_id, description in tags.items():
            tag_name = description["name"]
            if tag_name.startswith("ZZZTest"):
                continue
            tag_type = _tag_type_map[description["type"]]
            yield f"  {tag_name} ({tag_type})"


ExifTag.__doc__ = "\n".join(
    itertools.chain(
        [str(ExifTag.__doc__), "Available tag names:"],
        sorted(set(_generate_exif_tag_list())),
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

        exif_dict = piexif.load(str(file.absolute_path))
        try:
            latitude = extract_exif_value(exif_dict, "GPSLatitude")
            latitude_ref = extract_exif_value(exif_dict, "GPSLatitudeRef")
            longitude = extract_exif_value(exif_dict, "GPSLongitude")
            longitude_ref = extract_exif_value(exif_dict, "GPSLongitudeRef")

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
