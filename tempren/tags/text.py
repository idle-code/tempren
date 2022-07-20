import re
from re import Pattern
from typing import List, Optional

from unidecode import unidecode

from tempren.path_generator import File
from tempren.template.tree_elements import Tag


class UnidecodeTag(Tag):
    """Replace special unicode characters in context with ASCII equivalents"""

    require_context = True

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        return unidecode(context)


class RemoveTag(Tag):
    """Remove parts of the context based on RegEx patterns"""

    require_context = True
    patterns: List[Pattern]

    def configure(self, *patterns: str, ignore_case: bool = False):  # type: ignore
        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE  # TODO: make this configurable?
        self.patterns = list(map(lambda p: re.compile(p, flags), patterns))

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        result = context
        for pattern in self.patterns:
            result = pattern.sub("", result)
        return result


class ReplaceTag(Tag):
    """Replaces regex pattern with specified replacement"""

    require_context = True
    pattern: Pattern
    replacement: str

    def configure(self, pattern: str, replacement: str):  # type: ignore
        # TODO: add ignore-case option?
        self.pattern = re.compile(pattern)
        self.replacement = replacement

    def process(self, file: File, context: Optional[str]) -> str:
        assert context
        return self.pattern.sub(self.replacement, context)


class CollapseTag(Tag):
    """Collapse specified repeating characters in context"""

    require_context = True
    pattern: Pattern

    def configure(self, characters: str = " "):  # type: ignore
        # TODO: check characters for empty string?
        self.pattern = re.compile(f"(?<=[{characters}])[{characters}]+")

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        return self.pattern.sub("", context)


class UpperTag(Tag):
    """Makes context uppercase"""

    require_context = True

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        return context.upper()


class LowerTag(Tag):
    """Makes context lowercase"""

    require_context = True

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        return context.lower()


class StripTag(Tag):
    """Removes dangling characters on the ends of provided context"""

    require_context = True
    strip_characters: str = " "
    left: bool = False
    right: bool = False

    def configure(self, strip_characters: str = strip_characters, left: bool = False, right: bool = False):  # type: ignore
        self.strip_characters = strip_characters
        self.left = left
        self.right = right

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        if self.left and not self.right:
            return context.lstrip(self.strip_characters)
        if self.right and not self.left:
            return context.rstrip(self.strip_characters)
        return context.strip(self.strip_characters)


class TrimTag(Tag):
    """Trims context to a specified width by cropping left/right side off

    If width is less than 0, trims abs(width) number of characters from the side context instead.
    """

    require_context = True
    width: int
    left: bool = False
    right: bool = False

    def configure(self, width: int, left: bool = False, right: bool = False):  # type: ignore
        assert (
            width != 0
        ), "specify positive width or negative number of characters to trim"
        self.width = width
        assert (
            not left or not right
        ), "left and right cannot be specified at the same time"
        assert left or right, "no trim direction specified - use left or right"
        self.left = left
        self.right = right

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        if self.left:
            return context[-self.width :]
        return context[: self.width]


class CapitalizeTag(Tag):
    """Capitalizes first letter of the context"""

    require_context = True

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        return context.capitalize()


class TitleTag(Tag):
    """Capitalizes first letter of every word in the context"""

    require_context = True

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        return context.title()


class PadTag(Tag):
    """Adds padding to the context to match specified width"""

    require_context = True
    width: int
    character: str = " "
    left: bool = False
    right: bool = False
    center: bool = False

    def configure(self, width: int, character: str = character, left: bool = False, right: bool = False):  # type: ignore
        assert width > 0, "width have to be positive integer"
        self.width = width
        assert len(character) == 1, "single character have to be provided for padding"
        self.character = character
        assert left or right
        self.left = left
        self.right = right

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        if len(context) >= self.width:
            return context

        if self.left and self.right:
            return context.center(self.width, self.character)
        if self.left:
            return context.rjust(self.width, self.character)
        else:
            return context.ljust(self.width, self.character)
