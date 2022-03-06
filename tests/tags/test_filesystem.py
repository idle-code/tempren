import datetime
import os.path
from pathlib import Path

from tempren.tags.filesystem import MTimeTag, SizeTag


class TestSizeTag:
    def test_accepts_no_context(self):
        tag = SizeTag()

        assert not tag.require_context

    def test_returns_file_size_in_bytes(self, text_data_dir: Path):
        tag = SizeTag()

        hello_size = tag.process(text_data_dir / "hello.txt", None)

        assert hello_size == 6


class TestMTimeTag:
    def test_accepts_no_context(self):
        tag = MTimeTag()

        assert not tag.require_context

    def test_returns_file_size_in_bytes(self, text_data_dir: Path):
        tag = MTimeTag()
        hello_path = text_data_dir / "hello.txt"
        # Update hello.txt mtime to some known value
        hello_stat = os.stat(hello_path)
        now = datetime.datetime.now()
        os.utime(hello_path, times=(hello_stat.st_atime, now.timestamp()))

        hello_mtime_str = tag.process(hello_path, None)

        hello_mtime = datetime.datetime.fromisoformat(hello_mtime_str)
        assert now == hello_mtime
