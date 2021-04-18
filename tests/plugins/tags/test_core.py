from pathlib import Path

import pytest

from tempren.plugins.tags.core import CountTag, DirnameTag, ExtTag


class TestCountTag:
    def test_accepts_no_context(self):
        tag = CountTag()

        assert not tag.require_context

    def test_negative_start(self):
        tag = CountTag()

        with pytest.raises(ValueError):
            tag.configure(start=-1)

    def test_zero_step(self):
        tag = CountTag()

        with pytest.raises(ValueError):
            tag.configure(step=0)

    def test_negative_width(self):
        tag = CountTag()

        with pytest.raises(ValueError):
            tag.configure(width=-1)

    def test_first_result_is_start(self, nonexistent_path: Path):
        tag = CountTag()
        tag.configure(start=123)

        result = tag.process(nonexistent_path, None)

        assert result == "123"

    def test_second_result_differs_by_step(self, nonexistent_path: Path):
        tag = CountTag()
        tag.configure(step=3)

        tag.process(nonexistent_path, None)
        result = tag.process(nonexistent_path, None)

        assert result == "3"

    def test_width_control_leading_zeros(self, nonexistent_path: Path):
        tag = CountTag()
        tag.configure(width=3)

        result = tag.process(nonexistent_path, None)

        assert result == "000"

    def test_width_overflow(self, nonexistent_path: Path):
        tag = CountTag()
        tag.configure(step=123, width=2)

        result = tag.process(nonexistent_path, None)
        assert result == "00"

        result = tag.process(nonexistent_path, None)
        assert result == "123"


class TestExtTag:
    def test_without_context_original_extension_is_used(self):
        tag = ExtTag()

        extension = tag.process(Path("test/file.foo"), None)

        assert extension == "foo"

    def test_no_extension_on_filename(self):
        tag = ExtTag()

        extension = tag.process(Path("test/file"), None)

        assert extension == ""

    def test_context_extension(self):
        tag = ExtTag()

        extension = tag.process(Path("test/file.foo"), "test/file.bar")

        assert extension == "bar"


class TestDirnameTag:
    def test_no_context(self):
        tag = DirnameTag()

        dirname = tag.process(Path("test/file.name"), None)

        assert dirname == "test"

    def test_no_parent_dir(self):
        tag = DirnameTag()

        dirname = tag.process(Path("file"), None)

        assert dirname == "."

    def test_context_extension(self):
        tag = DirnameTag()

        dirname = tag.process(Path("foo/file"), "bar/file")

        assert dirname == "bar"
