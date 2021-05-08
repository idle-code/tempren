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


class TestRemoveTag:
    def test_pattern_not_found(self, nonexistent_path: Path):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_path, "bar")

        assert result == "bar"

    def test_single_occurrence(self, nonexistent_path: Path):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_path, "foobar")

        assert result == "bar"

    def test_multiple_occurrences(self, nonexistent_path: Path):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_path, "foobarfoo")

        assert result == "bar"

    def test_case_sensitiveness(self, nonexistent_path: Path):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_path, "foobarFOO")

        assert result == "barFOO"

    def test_ignore_case(self, nonexistent_path: Path):
        tag = RemoveTag()
        tag.configure("foo", ignore_case=True)

        result = tag.process(nonexistent_path, "foobarFOO")

        assert result == "bar"

    def test_multiple_patterns(self, nonexistent_path: Path):
        tag = RemoveTag()
        tag.configure("foo", "spam")

        result = tag.process(nonexistent_path, "foobarspam")

        assert result == "bar"


class TestCollapseTag:
    def test_nothing_to_collapse(self, nonexistent_path: Path):
        tag = CollapseTag()
        tag.configure()

        result = tag.process(nonexistent_path, "foobar")

        assert result == "foobar"

    def test_spaces_by_default(self, nonexistent_path: Path):
        tag = CollapseTag()
        tag.configure()

        result = tag.process(nonexistent_path, "foo   bar")

        assert result == "foo bar"

    def test_define_characters_to_collapse(self, nonexistent_path: Path):
        tag = CollapseTag()
        tag.configure("oz")

        result = tag.process(nonexistent_path, "foobazz")

        assert result == "fobaz"


class TestUpperTag:
    def test_makes_context_upper(self, nonexistent_path: Path):
        tag = UpperTag()

        result = tag.process(nonexistent_path, "upper")

        assert result == "UPPER"


class TestLowerTag:
    def test_makes_context_upper(self, nonexistent_path: Path):
        tag = LowerTag()

        result = tag.process(nonexistent_path, "LOWER")

        assert result == "lower"
