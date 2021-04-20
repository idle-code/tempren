import re
from pathlib import Path
from re import Pattern
from typing import Optional

from unidecode import unidecode

from tempren.template.tree_elements import Tag


class UnidecodeTag(Tag):
    require_context = True

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is not None
        return unidecode(context)


class RemoveTag(Tag):
    require_context = True
    patterns: [Pattern]

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
