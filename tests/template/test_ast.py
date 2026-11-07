import pytest

from tempren.exceptions import FileNotSupportedError, MissingMetadataError
from tempren.primitives import File, QualifiedTagName
from tempren.template.ast import RawText, TagInstance
from tempren.template.evaluation_context import (
    EvaluationContext,
    IgnoreMissingMetadata,
    propagate_errors,
)

from ..conftest import pattern_from
from .mocks import GeneratorTag, MockTag


class TestRawText:
    def test_text(self, nonexistent_file: File):
        element = RawText("text")

        assert element.process(nonexistent_file, propagate_errors) == "text"

    def test_empty(self, nonexistent_file: File):
        element = RawText("")

        assert element.process(nonexistent_file, propagate_errors) == ""


class TestPattern:
    def test_no_elements(self, nonexistent_file: File):
        element = pattern_from()

        assert element.process(nonexistent_file, propagate_errors) == ""

    def test_single_element(self, nonexistent_file: File):
        element = pattern_from(RawText("text"))

        assert element.process(nonexistent_file, propagate_errors) == "text"

    def test_concatenate_many(self, nonexistent_file: File):
        element = pattern_from(RawText("foo"), RawText("bar"))

        assert element.process(nonexistent_file, propagate_errors) == "foobar"

    def test_expression_string_rendering(self, nonexistent_file: File):
        mock_tag = MockTag(process_output="foo")
        element = pattern_from(TagInstance(tag=mock_tag), RawText(" == 'bar'"))

        assert (
            element.process_as_expression(nonexistent_file, propagate_errors)
            == "'foo' == 'bar'"
        )

    def test_path_value_rendering(self, nonexistent_file: File):
        mock_tag = MockTag(process_output=nonexistent_file.relative_path)
        element = pattern_from(TagInstance(tag=mock_tag))

        assert element.process(nonexistent_file, propagate_errors) == str(
            nonexistent_file.relative_path
        )

    def test_missing_metadata_error_rendering(self, nonexistent_file: File):
        def _tag_implementation(file, context):
            raise MissingMetadataError()

        throwing_tag = GeneratorTag(_tag_implementation)
        element = pattern_from(
            RawText("foo"), TagInstance(tag=throwing_tag), RawText("bar")
        )

        assert element.process(nonexistent_file, IgnoreMissingMetadata()) == "foobar"


class TestTagInstance:
    def test_file_is_passed_to_tag_implementation(self, nonexistent_file: File):
        file = nonexistent_file
        mock_tag = MockTag()
        element = TagInstance(tag=mock_tag)

        element.process(file, propagate_errors)

        assert mock_tag.file == file

    def test_context_is_processed_if_present(self, nonexistent_file: File):
        file = nonexistent_file
        context_tag = MockTag()
        context_pattern = pattern_from(TagInstance(tag=context_tag))
        element = TagInstance(tag=MockTag(), context=context_pattern)

        element.process(file, propagate_errors)

        assert context_tag.process_invoked

    def test_context_is_passed_to_tag_implementation(self, nonexistent_file: File):
        file = nonexistent_file
        context_tag = MockTag(process_output="Context output")
        outer_tag = MockTag()
        context_pattern = pattern_from(TagInstance(tag=context_tag))
        element = TagInstance(tag=outer_tag, context=context_pattern)

        element.process(file, propagate_errors)

        assert outer_tag.context == "Context output"

    def test_missing_metadata_error_is_handled(self, nonexistent_file: File):
        def _tag_implementation(file, context):
            raise MissingMetadataError()

        throwing_tag = GeneratorTag(_tag_implementation)
        element = TagInstance(tag=throwing_tag)

        assert element.process(nonexistent_file, IgnoreMissingMetadata()) == ""

    def test_metadata_error_is_propagated_by_default_context(
        self, nonexistent_file: File
    ):
        def _tag_implementation(file, context):
            raise FileNotSupportedError()

        element = TagInstance(tag=GeneratorTag(_tag_implementation))

        with pytest.raises(FileNotSupportedError):
            element.process(nonexistent_file, propagate_errors)

    def test_context_receives_tag_name(self, nonexistent_file: File):
        class RecordingContext(EvaluationContext):
            def handle_metadata_error(self, file, tag_name, error):
                return f"{file}:{tag_name}:{type(error).__name__}"

        def _tag_implementation(file, context):
            raise MissingMetadataError()

        element = TagInstance(
            tag=GeneratorTag(_tag_implementation),
            tag_name=QualifiedTagName("Width", "Image"),
        )

        assert (
            element.process(nonexistent_file, RecordingContext())
            == f"{nonexistent_file}:Image.Width:MissingMetadataError"
        )

    def test_not_supported_file_is_not_ignored(self, nonexistent_file: File):
        def _tag_implementation(file, context):
            raise FileNotSupportedError()

        element = TagInstance(tag=GeneratorTag(_tag_implementation))

        with pytest.raises(FileNotSupportedError):
            element.process(nonexistent_file, IgnoreMissingMetadata())
