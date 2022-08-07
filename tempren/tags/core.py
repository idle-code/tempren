import mimetypes
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional, Union

import magic
import pathvalidate

from tempren.template.path_generators import File
from tempren.template.tree_elements import Tag

mimetypes.init()


class CountTag(Tag):
    """Generates sequential numbers for each invocation"""

    require_context = False
    step: int
    width: int
    _common_counter: Optional[int] = None
    _per_directory_counters: defaultdict

    def configure(self, start: int = 0, step: int = 1, width: int = 0, common: bool = False):  # type: ignore
        """
        :param start: first element of generated sequence
        :param step: step added to previous element on each invocation
        :param width: number of characters taken by the number (will be zero-filled)
        :param common: use a single, global counter instead of per-directory ones

        If width is greater than zero, output will be a string value.
        """
        if start < 0:
            raise ValueError("start have to be greater or equal 0")
        if step == 0:
            raise ValueError("step cannot be equal 0")
        self.step = step
        if width < 0:
            raise ValueError("width have to be greater or equal 0")
        self.width = width
        if common:
            self._common_counter = start
        self._per_directory_counters = defaultdict(lambda: start)

    def process(self, file: File, context: Optional[str]) -> Union[str, int]:
        value = self._get_counter_value_for(file)
        if self.width != 0:
            return str(value).zfill(self.width)
        return value

    def _get_counter_value_for(self, file: File) -> int:
        directory = file.absolute_path.parent
        if self._common_counter is not None:
            value = self._common_counter
            self._common_counter += self.step
        else:
            value = self._per_directory_counters[directory]
            self._per_directory_counters[directory] += self.step
        if value < 0:
            raise ValueError(f"Invalid counter value generated: {value}")
        return value


class ExtTag(Tag):
    """File extension (with leading dot)

    If no context is provided, current file path is used and extension is extracted from it.
    If context is present, it is parsed as a path and file extension is extracted from it.
    """

    require_context = None

    def process(self, file: File, context: Optional[str]) -> str:
        if context:
            return str(Path(context).suffix)
        return str(file.relative_path.suffix)


class BaseTag(Tag):
    """Base file name without extension (suffix)

    If no context is provided, current file path is used to determine the base file name.
    If context is present, it is parsed as a path and file name is extracted from it.
    """

    require_context = None

    def process(self, file: File, context: Optional[str]) -> str:
        if context:
            return Path(context).stem
        return file.relative_path.stem


class DirTag(Tag):
    """Directory containing processed file

    If no context is provided, current file path is used to determine the parent directory.
    If context is present, it is parsed as a path to extract the parent directory.
    """

    require_context = None

    def process(self, file: File, context: Optional[str]) -> Path:
        if context:
            return Path(context).parent
        return file.relative_path.parent


class NameTag(Tag):
    """File name (basename with extension)"""

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


class MimeTag(Tag):
    """MIME type of processed file"""

    require_context = False
    select_type: bool = False
    select_subtype: bool = False

    def configure(self, type: bool = False, subtype: bool = False):  # type: ignore
        """
        :param type: return just type section of the mime type
        :param subtype: return just subtype section of the mime type
        """
        self.select_type = type
        self.select_subtype = subtype

    def process(self, file: File, context: Optional[str]) -> str:
        mime_type = magic.from_file(file.absolute_path, mime=True)
        if self.select_type and not self.select_subtype:
            return mime_type.split("/")[0]
        elif not self.select_type and self.select_subtype:
            return mime_type.split("/")[1]
        return mime_type


class MimeExtTag(Tag):
    """File extension guessed from MIME type"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> str:
        mime_type = magic.from_file(file.absolute_path, mime=True)
        return str(mimetypes.guess_extension(mime_type, False))


class IsMimeTag(Tag):
    """Checks if processed file MIME type matches provided value"""

    require_context = False
    expected_type_prefix: str

    def configure(self, type_prefix: str):  # type: ignore
        """
        :param type_prefix: expected MIME type
        :returns: True if file MIME type starts with expected value, False otherwise
        """
        self.expected_type_prefix = type_prefix

    def process(self, file: File, context: Optional[str]) -> Any:
        mime_type = magic.from_file(file.absolute_path, mime=True)
        return mime_type.startswith(self.expected_type_prefix)


class DefaultTag(Tag):
    """Returns default value if context is empty"""

    require_context = True

    default_value: Any

    def configure(self, default_value):  # type: ignore
        """
        :param default_value: value to be used if the context is empty or consists only of whitespace
        """
        self.default_value = default_value

    def process(self, file: File, context: Optional[str]) -> Any:
        if context and not context.isspace():
            return context
        return self.default_value
