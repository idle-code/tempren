from pathlib import Path

import pytest
from tempren.plugins.tags.core import CountTag


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
