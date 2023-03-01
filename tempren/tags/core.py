import datetime
import mimetypes
from collections import defaultdict
from math import ceil, floor
from pathlib import Path
from typing import Any, Optional, Union

import isodate
import magic
import pathvalidate
import pint as pint

from tempren.evaluation import evaluate_expression
from tempren.primitives import File, Tag

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
    If file doesn't have an extension, an empty string will be rendered.
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


class AsSizeTag(Tag):
    """Change size (in bytes) representation

    Supported unit prefixes are: K, M, G, T and P
    """

    require_context = True

    target_unit_multiplier: int
    precision_digits: Optional[int]

    _unit_weights = {
        "k": 1024,
        "m": 1024**2,
        "g": 1024**3,
        "t": 1024**4,
        "p": 1024**5,
    }

    def configure(self, unit: str, ndigits: Optional[int] = None):  # type: ignore
        """
        :param unit: name of the target unit
        :param ndigits: number of decimal digits
        """
        unit = str(unit).lower()
        unit_prefix = next(
            filter(
                lambda prefix: unit.startswith(prefix), AsSizeTag._unit_weights.keys()
            ),
            None,
        )
        if unit_prefix is None:
            raise ValueError("Unknown unit provided")
        self.target_unit_multiplier = AsSizeTag._unit_weights[unit_prefix]
        if ndigits is not None and ndigits <= 0:
            raise ValueError("Precision have to be positive")
        self.precision_digits = ndigits

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        size_in_bytes = float(context)
        size_in_target_unit = size_in_bytes / self.target_unit_multiplier
        size_in_target_unit = round(size_in_target_unit, self.precision_digits)
        return str(size_in_target_unit)


class RoundTag(Tag):
    """Round provided numeric value to specified number of decimal digits"""

    require_context = True

    precision_digits: int
    direction: Optional[bool]

    def configure(self, ndigits: int = 0, down: bool = False, up: bool = False):  # type: ignore
        """
        :param ndigits: number of decimal digits
        :param down: round to the closest integer less than the processed value
        :param up: round to the closest integer greater than the processed value
        """
        if ndigits != 0 and (down or up):
            raise ValueError("down or up cannot be used with precision digits")
        if down and up:
            raise ValueError("down and up cannot cannot be specified simultaneously")
        if down:
            self.direction = False
        elif up:
            self.direction = True
        else:
            self.direction = None
        self.precision_digits = ndigits

    def process(self, file: File, context: Optional[str]) -> Any:
        assert context is not None
        number = float(context)
        if self.direction is None:
            rounded_number = round(number, self.precision_digits)
            if self.precision_digits <= 0:
                rounded_number = int(rounded_number)
        elif self.direction:
            rounded_number = ceil(number)
        else:
            rounded_number = floor(number)
        return str(rounded_number)


class EvalTag(Tag):
    """Evaluate context as a Python expression"""

    require_context = True

    def process(self, file: File, context: Optional[str]) -> Any:  # type ignore
        assert context is not None
        return evaluate_expression(context)


class AsTimeTag(Tag):
    """Re-format provided date-time (in ISO 8601 representation)"""

    require_context = True

    destination_format: str

    def configure(self, format: str):  # type: ignore
        """
        :param format: strftime format to use
        """
        self.destination_format = format

    def process(self, file: File, context: Optional[str]) -> str:  # type: ignore
        assert context is not None
        parsed_datetime = datetime.datetime.fromisoformat(context)
        return parsed_datetime.strftime(self.destination_format)


AsTimeTag.__doc__ = "\n".join(
    [
        str(AsTimeTag.__doc__),
        """Possible fields:
Date
  %a\t Abbreviated weekday name ("Mon")
  %A\t Weekday name ("Monday")
  %b\t Abbreviated month name ("Oct")
  %B\t Month name ("October")
  %d\t Zero-prefixed day of the month (01..31)
  %e\t Day of the month (1..31)
  %j\t Zero-prefixed day of the year (001..366)
  %m\t Zero-prefixed month of the year (01..12)
  %U\t Week number of the current year (with Sunday being first day of the week) (00..53)
  %W\t Week number of the current year (with Monday being first day of the week) (00..53)
  %w\t Day of the week (where Sunday is 0) (0..6)
  %x\t System dependent representation for the date alone
  %y\t Year without a century (00..99)
  %Y\t Year with a century

Time
  %H\t Zero-prefixed hour (00..23)
  %I\t Zero-prefixed hour (01..12)
  %l\t Hour (1..12)
  %M\t Zero-prefixed minutes (00..59)
  %N\t Fractional seconds digits, default is 9 digits (nanosecond)
  %P\t Meridian indicator (am/pm)
  %p\t Meridian indicator (AM/PM)
  %S\t Zero-prefixed Seconds (00..60)
  %X\t System dependent representation for the time alone
  %Z\t Time zone name

Other
  %c\t System dependent date and time representation
  %%\t "%" character itself""",
    ]
)


class AsDurationTag(Tag):
    """Re-format provided duration (in ISO 8601 representation)"""

    require_context = True

    destination_format: str

    def configure(self, format: str):  # type: ignore
        """
        :param format: strftime format to use
        """
        self.destination_format = format

    def process(self, file: File, context: Optional[str]) -> str:  # type: ignore
        assert context is not None
        parsed_duration = isodate.parse_duration(context)
        return isodate.strftime(parsed_duration, self.destination_format)


AsDurationTag.__doc__ = "\n".join(
    [
        str(AsDurationTag.__doc__),
        """Possible fields:
  %j\t Zero-prefixed day of the year (001..366)
  %d\t Zero-prefixed day of the month (01..31)
  %m\t Zero-prefixed month (01..12)
  %W\t Week number of the current year (with Monday being first day of the week) (00..53)
  %w\t Day of the week (where Monday is 0) (0..6)
  %Y\t Year with a century (four digits)
  %C\t Century (00..99)
  %H\t Zero-prefixed hour (00..23)
  %M\t Zero-prefixed minutes (00..59)
  %S\t Zero-prefixed seconds (00..61)
  %f\t Zero-prefixed microsecond (0..999999)
  %z\t UTC offset in the form +HHMM or -HHMM (if present)
  %Z\t Time zone name (if present)
  %P\t ISO8601 duration format
  %p\t ISO8601 duration format in weeks
  %%\t "%" character itself""",
    ]
)


_supported_bases = {2: "b", 8: "o", 10: "d", 16: "x"}


class AsIntTag(Tag):
    """Converts integer from the context from one base to another (removing leading zeros if necessary)"""

    require_context = True

    src_base: int
    dst_base: int

    def configure(self, src_base: int = 10, dst_base: int = 10):  # type: ignore
        """
        :param src_base: source base
        :param dst_base: destination base
        Supported bases are: 2, 8, 10 and 16
        """
        if src_base not in _supported_bases:
            raise ValueError(f"Unsupported source base: {src_base}")
        if dst_base not in _supported_bases:
            raise ValueError(f"Unsupported destination base: {dst_base}")
        self.src_base = src_base
        self.dst_base = dst_base

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None

        parsed_number = int(context, base=self.src_base)
        return format(parsed_number, _supported_bases[self.dst_base])


class AsDistanceTag(Tag):
    """Re-format provided distance (in meters)"""

    require_context = True

    _dst_unit: pint.Unit
    _src_unit: pint.Unit

    _ureg_instance: Optional[pint.UnitRegistry] = None

    @property
    def _ureg(self) -> pint.UnitRegistry:
        if self._ureg_instance is None:
            self._ureg_instance = pint.UnitRegistry()
        return self._ureg_instance

    # noinspection PyMethodOverriding
    def configure(self, dst_unit: str, src_unit: str = "meter"):  # type: ignore
        """
        :param dst_unit: unit name to convert to
        :param src_unit: source value unit name

        """
        self._dst_unit = self._ureg.parse_units(dst_unit)
        self._src_unit = self._ureg.parse_units(src_unit)

    def process(self, file: File, context: Optional[str]) -> float:
        assert context is not None
        src_value = float(context) * self._src_unit
        dst_value = src_value.to(self._dst_unit)
        return dst_value.magnitude
