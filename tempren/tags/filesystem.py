import datetime
import os.path
from pathlib import Path
from typing import Any, Optional

from tempren.template.tree_elements import Tag


class SizeTag(Tag):
    """Returns file size in bytes"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> int:
        assert context is None
        return os.path.getsize(path)


class MTimeTag(Tag):
    """Returns file modification time (in ISO 8601 format)"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> Any:
        assert context is None
        mtime_seconds = os.path.getmtime(path)
        mtime = datetime.datetime.fromtimestamp(mtime_seconds)
        return mtime.isoformat()
