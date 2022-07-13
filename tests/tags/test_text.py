import pytest

from tempren.path_generator import File
from tempren.tags.text import (
    CapitalizeTag,
    CollapseTag,
    LowerTag,
    PadTag,
    RemoveTag,
    ReplaceTag,
    StripTag,
    TitleTag,
    TrimTag,
    UnidecodeTag,
    UpperTag,
)


class TestUnidecodeTag:
    def test_ascii_input_unchanged(self, nonexistent_file: File):
        tag = UnidecodeTag()

        result = tag.process(nonexistent_file, "Foo Bar.spam")

        assert result == "Foo Bar.spam"

    def test_polish_characters_are_normalized(self, nonexistent_file: File):
        tag = UnidecodeTag()

        result = tag.process(nonexistent_file, "Zażółć gęślą jaźń")

        assert result == "Zazolc gesla jazn"

    def test_emoticons_are_removed(self, nonexistent_file: File):
        tag = UnidecodeTag()

        result = tag.process(nonexistent_file, "Some|😴☯😸❓🇨🇭🌌|emotes")

        assert result == "Some||emotes"


class TestRemoveTag:
    def test_pattern_not_found(self, nonexistent_file: File):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_file, "bar")

        assert result == "bar"

    def test_single_occurrence(self, nonexistent_file: File):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_file, "foobar")

        assert result == "bar"

    def test_multiple_occurrences(self, nonexistent_file: File):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_file, "foobarfoo")

        assert result == "bar"

    def test_case_sensitiveness(self, nonexistent_file: File):
        tag = RemoveTag()
        tag.configure("foo")

        result = tag.process(nonexistent_file, "foobarFOO")

        assert result == "barFOO"

    def test_ignore_case(self, nonexistent_file: File):
        tag = RemoveTag()
        tag.configure("foo", ignore_case=True)

        result = tag.process(nonexistent_file, "foobarFOO")

        assert result == "bar"

    def test_multiple_patterns(self, nonexistent_file: File):
        tag = RemoveTag()
        tag.configure("foo", "spam")

        result = tag.process(nonexistent_file, "foobarspam")

        assert result == "bar"


class TestReplaceTag:
    def test_pattern_not_found(self, nonexistent_file: File):
        tag = ReplaceTag()
        tag.configure("foo", "bar")

        result = tag.process(nonexistent_file, "spam")

        assert result == "spam"

    def test_single_replacement(self, nonexistent_file: File):
        tag = ReplaceTag()
        tag.configure("foo", "bar")

        result = tag.process(nonexistent_file, "foobar")

        assert result == "barbar"

    def test_multiple_replacements(self, nonexistent_file: File):
        tag = ReplaceTag()
        tag.configure("foo", "bar")

        result = tag.process(nonexistent_file, "foobarfoo")

        assert result == "barbarbar"

    def test_replace_pattern(self, nonexistent_file: File):
        tag = ReplaceTag()
        tag.configure("o+", "bar")

        result = tag.process(nonexistent_file, "foobar")

        assert result == "fbarbar"

    def test_replace_with_capture(self, nonexistent_file: File):
        tag = ReplaceTag()
        tag.configure("f(o+)", "\\1 \\1 ")

        result = tag.process(nonexistent_file, "foobar")

        assert result == "oo oo bar"


class TestCollapseTag:
    def test_nothing_to_collapse(self, nonexistent_file: File):
        tag = CollapseTag()
        tag.configure()

        result = tag.process(nonexistent_file, "foobar")

        assert result == "foobar"

    def test_spaces_by_default(self, nonexistent_file: File):
        tag = CollapseTag()
        tag.configure()

        result = tag.process(nonexistent_file, "foo   bar")

        assert result == "foo bar"

    def test_define_characters_to_collapse(self, nonexistent_file: File):
        tag = CollapseTag()
        tag.configure("oz")

        result = tag.process(nonexistent_file, "foobazz")

        assert result == "fobaz"


class TestUpperTag:
    def test_makes_context_upper(self, nonexistent_file: File):
        tag = UpperTag()

        result = tag.process(nonexistent_file, "upper")

        assert result == "UPPER"


class TestLowerTag:
    def test_makes_context_upper(self, nonexistent_file: File):
        tag = LowerTag()

        result = tag.process(nonexistent_file, "LOWER")

        assert result == "lower"


class TestStripTag:
    def test_strip_spaces_on_both_ends(self, nonexistent_file: File):
        tag = StripTag()

        result = tag.process(nonexistent_file, "  foobar ")

        assert result == "foobar"

    def test_strip_provided_chars_on_both_ends(self, nonexistent_file: File):
        tag = StripTag()
        tag.configure("_.")

        result = tag.process(nonexistent_file, "__foobar..")

        assert result == "foobar"

    def test_left_strip_spaces(self, nonexistent_file: File):
        tag = StripTag()
        tag.configure(left=True)

        result = tag.process(nonexistent_file, "  foobar  ")

        assert result == "foobar  "

    def test_right_strip_spaces(self, nonexistent_file: File):
        tag = StripTag()
        tag.configure(right=True)

        result = tag.process(nonexistent_file, "  foobar  ")

        assert result == "  foobar"

    def test_left_and_right_strip_spaces(self, nonexistent_file: File):
        tag = StripTag()
        tag.configure(left=True, right=True)

        result = tag.process(nonexistent_file, "  foobar  ")

        assert result == "foobar"


class TestTrimTag:
    def test_trims_right(self, nonexistent_file: File):
        tag = TrimTag()
        tag.configure(4, right=True)

        result = tag.process(nonexistent_file, "0123456789")

        assert result == "0123"

    def test_trims_left(self, nonexistent_file: File):
        tag = TrimTag()
        tag.configure(4, left=True)

        result = tag.process(nonexistent_file, "0123456789")

        assert result == "6789"

    def test_trims_negative_right(self, nonexistent_file: File):
        tag = TrimTag()
        tag.configure(-4, right=True)

        result = tag.process(nonexistent_file, "0123456789")

        assert result == "012345"

    def test_trims_negative_left(self, nonexistent_file: File):
        tag = TrimTag()
        tag.configure(-4, left=True)

        result = tag.process(nonexistent_file, "0123456789")

        assert result == "456789"

    def test_no_trim_direction_misconfiguration(self):
        tag = TrimTag()

        with pytest.raises(AssertionError):
            tag.configure(4)

    def test_both_trims_misconfiguration(self):
        tag = TrimTag()

        with pytest.raises(AssertionError):
            tag.configure(4, left=True, right=True)

    def test_width_misconfiguration(self):
        tag = TrimTag()

        with pytest.raises(AssertionError):
            tag.configure(0, left=True)


class TestCapitalizeTag:
    def test_capitalize(self, nonexistent_file: File):
        tag = CapitalizeTag()

        result = tag.process(nonexistent_file, "Foo Bar SPAM")

        assert result == "Foo bar spam"

    @pytest.mark.skip("May not be necessary")
    def test_capitalize_with_whitespace(self, nonexistent_file: File):
        tag = CapitalizeTag()

        result = tag.process(nonexistent_file, "  foo bar SPAM ")

        assert result == "  Foo bar spam "


class TestTitleTag:
    def test_title(self, nonexistent_file: File):
        tag = TitleTag()

        result = tag.process(nonexistent_file, "foo bar SPAM")

        assert result == "Foo Bar Spam"

    def test_title_with_whitespace(self, nonexistent_file: File):
        tag = TitleTag()

        result = tag.process(nonexistent_file, "  foo bar SPAM ")

        assert result == "  Foo Bar Spam "


class TestPadTag:
    def test_pads_right(self, nonexistent_file: File):
        tag = PadTag()
        tag.configure(6, right=True)

        result = tag.process(nonexistent_file, "0123")

        assert result == "0123  "

    def test_pads_left(self, nonexistent_file: File):
        tag = PadTag()
        tag.configure(6, left=True)

        result = tag.process(nonexistent_file, "0123")

        assert result == "  0123"

    def test_pads_center(self, nonexistent_file: File):
        tag = PadTag()
        tag.configure(6, left=True, right=True)

        result = tag.process(nonexistent_file, "0123")

        assert result == " 0123 "

    def test_pads_larger(self, nonexistent_file: File):
        tag = PadTag()
        tag.configure(6, left=True)

        result = tag.process(nonexistent_file, "012345")

        assert result == "012345"

    def test_pads_custom_character(self, nonexistent_file: File):
        tag = PadTag()
        tag.configure(6, "_", left=True)

        result = tag.process(nonexistent_file, "0123")

        assert result == "__0123"

    def test_no_custom_characters_misconfiguration(self):
        tag = PadTag()

        with pytest.raises(AssertionError):
            tag.configure(6, "_.", left=True)

    def test_too_many_custom_character_misconfiguration(self):
        tag = PadTag()

        with pytest.raises(AssertionError):
            tag.configure(6, "", left=True)

    def test_no_padding_direction_misconfiguration(self):
        tag = PadTag()

        with pytest.raises(AssertionError):
            tag.configure(4)

    def test_width_misconfiguration(self):
        tag = PadTag()

        with pytest.raises(AssertionError):
            tag.configure(0, left=True)

        with pytest.raises(AssertionError):
            tag.configure(-2, left=True)
