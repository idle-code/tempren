import os.path
from pathlib import Path
from typing import Optional

from tempren.template.tree_elements import Tag


class SizeTag(Tag):
    """Returns file size in bytes"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> int:
        assert context is None
        return os.path.getsize(path)
