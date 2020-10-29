from pytest import raises
from tempren.template.tree_elements import Pattern, RawText, TagPlaceholder


class TestRawText:
    def test_text(self):
        element = RawText("text")

        assert str(element) == "text"

    def test_empty(self):
        element = RawText("")

        assert str(element) == ""


class TestPattern:
    def test_no_elements(self):
        element = Pattern()

        assert str(element) == ""

    def test_single_element(self):
        element = Pattern([RawText("text")])

        assert str(element) == "text"

    def test_concatenate_many(self):
        element = Pattern([RawText("foo"), RawText("bar")])

        assert str(element) == "foobar"


class TestTagPlaceholder:
    def test_invalid_tag_name(self):
        with raises(ValueError):
            TagPlaceholder("")
