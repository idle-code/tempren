import datetime
import os.path
from typing import Any, Optional

from tempren.primitives import File, Tag


class SizeTag(Tag):
    """File size in bytes"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> int:
        assert context is None
        return os.path.getsize(file.absolute_path)


class MTimeTag(Tag):
    """File modification time (in ISO 8601 format)"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> Any:
        assert context is None
        mtime_seconds = os.path.getmtime(file.absolute_path)
        mtime = datetime.datetime.fromtimestamp(mtime_seconds)
        return mtime.isoformat()


class OwnerTag(Tag):
    """Name of the user owning processed file"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> str:
        # TODO: Maybe if context is present parse it as a path?
        return file.absolute_path.owner()


class GroupTag(Tag):
    """Name of the group owning processed file"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> str:
        # TODO: Maybe if context is present parse it as a path?
        return file.absolute_path.group()
