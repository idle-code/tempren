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


class EntryCountTag(Tag):
    """Number of entries (files and directories) in the processed directory

    In directory mode, processed directory means the one being renamed.
    In name and path modes, parent directory entry count is used instead.
    """

    require_context = False

    def process(self, file: File, context: Optional[str]) -> int:
        if file.absolute_path.is_dir():
            target_directory = file.absolute_path
        else:
            target_directory = file.absolute_path.parent

        # CHECK: How hidden files should be counted?
        return len(os.listdir(target_directory))
