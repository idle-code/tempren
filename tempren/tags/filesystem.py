import datetime
import os.path
from typing import Any, Optional

from tempren.path_generator import File
from tempren.template.tree_elements import Tag


class SizeTag(Tag):
    """Returns file size in bytes"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> int:
        assert context is None
        return os.path.getsize(file.absolute_path)


class MTimeTag(Tag):
    """Returns file modification time (in ISO 8601 format)"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> Any:
        assert context is None
        mtime_seconds = os.path.getmtime(file.absolute_path)
        mtime = datetime.datetime.fromtimestamp(mtime_seconds)
        return mtime.isoformat()
