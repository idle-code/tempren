from pathlib import Path

from pytest import raises
from tempren.template.tree_elements import Pattern, RawText, TagInstance, TagPlaceholder

from .mocks import MockTag


class TestRawText:
    def test_text(self, nonexistent_path: Path):
        element = RawText("text")

        assert element.process(nonexistent_path) == "text"

    def test_empty(self, nonexistent_path: Path):
        element = RawText("")

        assert element.process(nonexistent_path) == ""


class TestPattern:
    def test_no_elements(self, nonexistent_path: Path):
        element = Pattern()

        assert element.process(nonexistent_path) == ""

    def test_single_element(self, nonexistent_path: Path):
        element = Pattern([RawText("text")])

        assert element.process(nonexistent_path) == "text"

    def test_concatenate_many(self, nonexistent_path: Path):
        element = Pattern([RawText("foo"), RawText("bar")])

        assert element.process(nonexistent_path) == "foobar"


class TestTagPlaceholder:
    def test_invalid_tag_name(self):
        with raises(ValueError):
            TagPlaceholder("")


class TestTagInstance:
    def test_path_is_passed_to_tag_implementation(self, nonexistent_path: Path):
        path = nonexistent_path
        mock_tag = MockTag()
        element = TagInstance(tag=mock_tag)

        element.process(path)

        assert mock_tag.path == path

    def test_context_is_processed_if_present(self, nonexistent_path: Path):
        path = nonexistent_path
        context_tag = MockTag()
        context_pattern = Pattern([TagInstance(tag=context_tag)])
        element = TagInstance(tag=MockTag(), context=context_pattern)

        element.process(path)

        assert context_tag.process_invoked

    def test_context_is_passed_to_tag_implementation(self, nonexistent_path: Path):
        path = nonexistent_path
        context_tag = MockTag(process_output="Context output")
        outer_tag = MockTag()
        context_pattern = Pattern([TagInstance(tag=context_tag)])
        element = TagInstance(tag=outer_tag, context=context_pattern)

        element.process(path)

        assert outer_tag.context == "Context output"
