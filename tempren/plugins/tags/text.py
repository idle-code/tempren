from pathlib import Path
from typing import Optional

from unidecode import unidecode

from tempren.template.tree_elements import Tag


class UnidecodeTag(Tag):
    require_context = True

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is not None
        return unidecode(context)
