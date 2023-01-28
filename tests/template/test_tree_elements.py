from pytest import raises

from tempren.path_generator import File
from tempren.template.ast import (
    MissingMetadataError,
    Pattern,
    RawText,
    TagInstance,
    TagName,
)

from .mocks import GeneratorTag, MockTag


class TestRawText:
    def test_text(self, nonexistent_file: File):
        element = RawText("text")

        assert element.process(nonexistent_file) == "text"

    def test_empty(self, nonexistent_file: File):
        element = RawText("")

        assert element.process(nonexistent_file) == ""


class TestPattern:
    def test_no_elements(self, nonexistent_file: File):
        element = Pattern()

        assert element.process(nonexistent_file) == ""

    def test_single_element(self, nonexistent_file: File):
        element = Pattern([RawText("text")])

        assert element.process(nonexistent_file) == "text"

    def test_concatenate_many(self, nonexistent_file: File):
        element = Pattern([RawText("foo"), RawText("bar")])

        assert element.process(nonexistent_file) == "foobar"

    def test_expression_string_rendering(self, nonexistent_file: File):
        mock_tag = MockTag(process_output="foo")
        element = Pattern([TagInstance(tag=mock_tag), RawText(" == 'bar'")])

        assert element.process_as_expression(nonexistent_file) == "'foo' == 'bar'"

    def test_path_value_rendering(self, nonexistent_file: File):
        mock_tag = MockTag(process_output=nonexistent_file.relative_path)
        element = Pattern([TagInstance(tag=mock_tag)])

        assert element.process(nonexistent_file) == str(nonexistent_file.relative_path)

    def test_missing_metadata_error_rendering(self, nonexistent_file: File):
        def _tag_implementation(file, context):
            raise MissingMetadataError()

        throwing_tag = GeneratorTag(_tag_implementation)
        element = Pattern(
            [RawText("foo"), TagInstance(tag=throwing_tag), RawText("bar")]
        )

        assert element.process(nonexistent_file) == "foobar"


class TestTagName:
    def test_invalid_tag_name(self):
        with raises(ValueError):
            TagName("")

    def test_invalid_tag_category(self):
        with raises(ValueError):
            TagName("TAG", "")


class TestTagInstance:
    def test_file_is_passed_to_tag_implementation(self, nonexistent_file: File):
        file = nonexistent_file
        mock_tag = MockTag()
        element = TagInstance(tag=mock_tag)

        element.process(file)

        assert mock_tag.file == file

    def test_context_is_processed_if_present(self, nonexistent_file: File):
        file = nonexistent_file
        context_tag = MockTag()
        context_pattern = Pattern([TagInstance(tag=context_tag)])
        element = TagInstance(tag=MockTag(), context=context_pattern)

        element.process(file)

        assert context_tag.process_invoked

    def test_context_is_passed_to_tag_implementation(self, nonexistent_file: File):
        file = nonexistent_file
        context_tag = MockTag(process_output="Context output")
        outer_tag = MockTag()
        context_pattern = Pattern([TagInstance(tag=context_tag)])
        element = TagInstance(tag=outer_tag, context=context_pattern)

        element.process(file)

        assert outer_tag.context == "Context output"

    def test_missing_metadata_error_is_handled(self, nonexistent_file: File):
        def _tag_implementation(file, context):
            raise MissingMetadataError()

        throwing_tag = GeneratorTag(_tag_implementation)
        element = TagInstance(tag=throwing_tag)

        assert element.process(nonexistent_file) == ""
