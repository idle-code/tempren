from pathlib import Path

import pytest

from tempren.plugins.tags.text import *


class TestUnidecodeTag:
    def test_ascii_input_unchanged(self, nonexistent_path: Path):
        tag = UnidecodeTag()

        result = tag.process(nonexistent_path, "Foo Bar.spam")

        assert result == "Foo Bar.spam"

    def test_polish_characters_are_normalized(self, nonexistent_path: Path):
        tag = UnidecodeTag()

        result = tag.process(nonexistent_path, "Zażółć gęślą jaźń")

        assert result == "Zazolc gesla jazn"

    def test_emoticons_are_removed(self, nonexistent_path: Path):
        tag = UnidecodeTag()

        result = tag.process(nonexistent_path, "Some|😴☯😸❓🆗🇨🇭🌌|emotes")

        assert result == "Some||emotes"
