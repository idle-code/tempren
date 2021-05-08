from pathlib import Path
from typing import Optional

import pathvalidate

from tempren.template.tree_elements import Tag


class CountTag(Tag):
    """Generates sequential numbers for each invocation"""

    require_context = False  # TODO: use enum for values
    counter: int
    step: int
    width: int

    def configure(self, start: int = 0, step: int = 1, width: int = 0):  # type: ignore
        if start < 0:
            raise ValueError("start have to be greater or equal 0")
        self.counter = start
        if step == 0:
            raise ValueError("step cannot be equal 0")
        self.step = step
        if width < 0:
            raise ValueError("width have to be greater or equal 0")
        self.width = width

    def process(self, path: Path, context: Optional[str]) -> str:
        value = self.counter
        self.counter += self.step
        return str(value).zfill(self.width)


class ExtTag(Tag):
    """Renders processed file extension"""

    require_context = None

    def process(self, path: Path, context: Optional[str]) -> str:
        if context:
            path = Path(context)
        return path.suffix.lstrip(".")


class BasenameTag(Tag):
    """Renders processed file name without extension"""

    require_context = None

    def process(self, path: Path, context: Optional[str]) -> str:
        if context:
            path = Path(context)
        return path.stem


class DirnameTag(Tag):
    """Renders file parent directory path"""

    require_context = None

    def process(self, path: Path, context: Optional[str]) -> str:
        if context:
            path = Path(context)
        return str(path.parent)


# TODO: Add option to omit file extension (for compatibility with ExtTag
class FilenameTag(Tag):
    """Renders processed file name"""

    require_context = None

    def process(self, path: Path, context: Optional[str]) -> str:
        if context:
            path = Path(context)
        return str(path.name)


class SanitizeTag(Tag):
    """Removes unsafe characters from provided context"""

    require_context = True

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context
        return str(pathvalidate.sanitize_filepath(context))
