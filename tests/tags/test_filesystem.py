import datetime
import os.path
from pathlib import Path

from tempren.primitives import File
from tempren.tags.filesystem import EntryCountTag, GroupTag, MTimeTag, OwnerTag, SizeTag


class TestSizeTag:
    def test_accepts_no_context(self):
        tag = SizeTag()

        assert not tag.require_context

    def test_returns_file_size_in_bytes(self, text_data_dir: Path):
        tag = SizeTag()
        hello_file = File(text_data_dir, Path("hello.txt"))

        hello_size = tag.process(hello_file, None)

        assert hello_size == 6


class TestMTimeTag:
    def test_accepts_no_context(self):
        tag = MTimeTag()

        assert not tag.require_context

    def test_returns_file_size_in_bytes(self, text_data_dir: Path):
        tag = MTimeTag()
        hello_file = File(text_data_dir, Path("hello.txt"))
        # Update hello.txt mtime to some known value
        hello_stat = os.stat(hello_file.absolute_path)
        now = datetime.datetime.now()
        os.utime(hello_file.absolute_path, times=(hello_stat.st_atime, now.timestamp()))

        hello_mtime_str = tag.process(hello_file, None)

        hello_mtime = datetime.datetime.fromisoformat(hello_mtime_str)
        assert now == hello_mtime


class TestOwnerTag:
    def test_file_owner(self, text_data_dir: Path):
        tag = OwnerTag()
        hello_file = File(text_data_dir, Path("hello.txt"))
        hello_owner = hello_file.absolute_path.owner()

        owner = tag.process(hello_file, None)

        assert hello_owner == owner


class TestGroupTag:
    def test_file_group(self, text_data_dir: Path):
        tag = GroupTag()
        hello_file = File(text_data_dir, Path("hello.txt"))
        hello_group = hello_file.absolute_path.group()

        group = tag.process(hello_file, None)

        assert hello_group == group


class TestEntryCountTag:
    def test_count_parent_entries_for_file(self, nested_data_dir: Path):
        tag = EntryCountTag()
        file = File(nested_data_dir, Path("level-1.txt"))

        entry_count = tag.process(file, None)

        assert entry_count == 3

    def test_entries_for_directory(self, nested_data_dir: Path):
        tag = EntryCountTag()
        nested_data_dir = File(nested_data_dir.parent, Path(nested_data_dir.name))

        entry_count = tag.process(nested_data_dir, None)

        assert entry_count == 3
