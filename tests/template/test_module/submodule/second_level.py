from pathlib import Path
from typing import Optional

from tempren.template.tree_elements import Tag


class SecondLevelTag(Tag):
    require_context = None

    def process(self, path: Path, context: Optional[str]) -> str:
        raise NotImplementedError()
