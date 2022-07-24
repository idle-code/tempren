from abc import ABC, abstractmethod
from typing import Any, Optional

import PIL
from PIL import Image

from tempren.path_generator import File
from tempren.template.tree_elements import (
    FileNotSupportedError,
    MissingMetadataError,
    Tag,
)


class PillowTag(Tag, ABC):
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


class WidthTag(PillowTag):
    """Image width in pixels"""

    def extract_metadata(self, image: Image) -> Any:
        return image.width


class HeightTag(PillowTag):
    """Image height in pixels"""

    def extract_metadata(self, image: Image) -> Any:
        return image.height
