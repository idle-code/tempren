from pathlib import Path
from typing import Optional

import pathvalidate

from tempren.template.path_generators import File
from tempren.template.tree_elements import Tag


class CountTag(Tag):
    """Generates sequential numbers for each invocation"""

    require_context = False
    counter: int
    step: int
    width: int

    def configure(self, start: int = 0, step: int = 1, width: int = 0):  # type: ignore
        """
        :param start: first element of generated sequence
        :param step: step added to previous element on each invocation
        :param width: number of characters taken by the number (will be zero-filled)
        """
        if start < 0:
            raise ValueError("start have to be greater or equal 0")
        self.counter = start
        if step == 0:
            raise ValueError("step cannot be equal 0")
        self.step = step
        if width < 0:
            raise ValueError("width have to be greater or equal 0")
        self.width = width

    def process(self, file: File, context: Optional[str]) -> str:
        value = self.counter
        self.counter += self.step
        return str(value).zfill(self.width)


class ExtTag(Tag):
    """Renders processed file extension

    If no context is provided, current file path is used and extension is extracted from it.
    If context is present, it is parsed as a path and file extension is extracted from it.
    """

    require_context = None

    def process(self, file: File, context: Optional[str]) -> str:
        if context:
            return str(Path(context).suffix).lstrip(".")
        return str(file.relative_path.suffix).lstrip(".")


class BasenameTag(Tag):
    """Renders base file name without extension (suffix)

    If no context is provided, current file path is used to determine the base file name.
    If context is present, it is parsed as a path and file name is extracted from it.
    """

    require_context = None

    def process(self, file: File, context: Optional[str]) -> str:
        if context:
            return Path(context).stem
        return file.relative_path.stem


class DirnameTag(Tag):
    """Renders file parent directory path

    If no context is provided, current file path is used to determine the parent directory.
    If context is present, it is parsed as a path to extract the parent directory.
    """

    require_context = None

    def process(self, file: File, context: Optional[str]) -> Path:
        if context:
            return Path(context).parent
        return file.relative_path.parent


class FilenameTag(Tag):
    """Renders processed file name (basename with extension)"""

    require_context = None

    def process(self, file: File, context: Optional[str]) -> str:
        if context:
            return str(Path(context).name)
        return str(file.relative_path.name)


class SanitizeTag(Tag):
    """Removes filesystem-unsafe characters from provided context"""

    require_context = True

    def process(self, file: File, context: Optional[str]) -> str:
        assert context
        return str(pathvalidate.sanitize_filepath(context))
