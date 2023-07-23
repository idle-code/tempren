import itertools
from abc import ABC, abstractmethod
from fractions import Fraction
from typing import Any, Iterator, Optional, Tuple

import piexif
import PIL
from piexif import TAGS
from piexif import TYPES as TAG_TYPES
from PIL import Image

from tempren.alias import TagAlias
from tempren.exceptions import FileNotSupportedError, MissingMetadataError
from tempren.primitives import File, Tag


class PillowTagBase(Tag, ABC):
    """Base for tags extracting metadata from images using Pillow library"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> Any:
        try:
            with Image.open(file.absolute_path) as img:
                return self.extract_metadata(img)
        except PIL.UnidentifiedImageError:
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


class ExifTag(Tag):
    """Extract value of any EXIF tag"""

    tag_id: int
    tag_type: int

    def configure(self, tag_name: str):  # type: ignore
        """
        :param tag_name: name of the tag to extract (e.g. 'FocalLength', 'DateTime', 'FNumber')
        """
        # TODO: generate list of supported tags dynamically
        assert tag_name, "expected non empty tag name"
        self.tag_id, self.tag_type = self._tag_name_to_id_type(tag_name)

    @staticmethod
    def _tag_name_to_id_type(tag_name: str) -> Tuple[int, int]:
        for _, tags in TAGS.items():
            for tag_id, description in tags.items():
                if description["name"] == tag_name:
                    return tag_id, description["type"]
        raise ValueError(f"Could not find tag id for '{tag_name}'")

    def process(self, file: File, context: Optional[str]) -> Any:
        exif_dict = piexif.load(str(file.absolute_path))
        for src in exif_dict.values():
            if isinstance(src, dict) and self.tag_id in src:
                return self._extract_value(src[self.tag_id])
        else:
            raise MissingMetadataError()

    def _extract_value(self, tag_value):
        if self.tag_type in (TAG_TYPES.Rational, TAG_TYPES.SRational):
            return round(tag_value[0] / tag_value[1], 1)
        if self.tag_type == TAG_TYPES.Ascii:
            return tag_value.decode("ascii")
        return tag_value


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
