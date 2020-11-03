from pathlib import Path

from pytest import raises
from tempren.template.tree_elements import Pattern, RawText, TagPlaceholder


class TestRawText:
    def test_text(self):
        path = Path("foo", "bar")
        element = RawText("text")

        assert element.process(path) == "text"

    def test_empty(self):
        path = Path("foo", "bar")
        element = RawText("")

        assert element.process(path) == ""


class TestPattern:
    def test_no_elements(self):
        path = Path("foo", "bar")
        element = Pattern()

        assert element.process(path) == ""

    def test_single_element(self):
        path = Path("foo", "bar")
        element = Pattern([RawText("text")])

        assert element.process(path) == "text"

    def test_concatenate_many(self):
        path = Path("foo", "bar")
        element = Pattern([RawText("foo"), RawText("bar")])

        assert element.process(path) == "foobar"


class TestTagPlaceholder:
    def test_invalid_tag_name(self):
        with raises(ValueError):
            TagPlaceholder("")
