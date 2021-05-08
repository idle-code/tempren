import re
from pathlib import Path
from re import Pattern
from typing import List, Optional

from unidecode import unidecode

from tempren.template.tree_elements import Tag


class UnidecodeTag(Tag):
    """Replace special unicode characters in context with ASCII equivalents"""

    require_context = True

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is not None
        return unidecode(context)


class RemoveTag(Tag):
    """Remove parts of the context based on RegEx patterns"""

    require_context = True
    patterns: List[Pattern]

    def configure(self, *patterns: str, ignore_case: bool = False):  # type: ignore
        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE
        self.patterns = list(map(lambda p: re.compile(p, flags), patterns))

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context
        result = context
        for pattern in self.patterns:
            result = pattern.sub("", result)
        return result


class CollapseTag(Tag):
    """Collapse specified repeating characters in context"""

    require_context = True
    pattern: Pattern

    def configure(self, characters: str = " "):  # type: ignore
        self.pattern = re.compile(f"(?<=[{characters}])[{characters}]+")

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context
        return self.pattern.sub("", context)
