from pathlib import Path

import pytest
from pytest import raises

from tempren.path_generator import File
from tempren.template.tree_elements import (
    AdHocTag,
    ExecutionTimeoutError,
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


class TestAdHocTag:
    def test_invalid_executable_path(self, nonexistent_absolute_path: Path):
        with pytest.raises(AssertionError):
            AdHocTag(nonexistent_absolute_path)

    def test_executable_is_invoked(self, text_data_dir: Path):
        new_file = File(text_data_dir, Path("new.file"))
        assert not new_file.absolute_path.exists()
        touch_tag = AdHocTag(Path("/usr/bin/touch"))

        result = touch_tag.process(new_file, None)

        assert result is ""
        assert new_file.absolute_path.exists()

    def test_stdout_is_returned(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        cat_tag = AdHocTag(Path("/usr/bin/cat"))

        result = cat_tag.process(hello_file, None)

        assert result == "Hello"

    def test_error_code_raises_error(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        false_tag = AdHocTag(Path("/usr/bin/false"))

        with pytest.raises(MissingMetadataError) as exc:
            false_tag.process(hello_file, None)

        assert exc.match(r"error code \(1\)")

    def test_positional_arguments_are_passed(self, text_data_dir: Path):
        markdown_file = File(text_data_dir, Path("markdown.md"))
        tail_tag = AdHocTag(Path("/usr/bin/tail"))
        tail_tag.configure("-n", "1")

        result = tail_tag.process(markdown_file, None)

        assert result == "Second, a bit longer paragraph."

    def test_context_replaces_file_argument(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        cat_tag = AdHocTag(Path("/usr/bin/cat"))

        result = cat_tag.process(hello_file, "foobar")

        assert result == "foobar"

    def test_executable_default_timeout(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        sleep_tag = AdHocTag(Path("/usr/bin/sleep"))
        sleep_tag.configure("4s")

        with pytest.raises(ExecutionTimeoutError) as exc:
            sleep_tag.process(hello_file, "")

        assert exc.match("timeout")

    def test_executable_explicit_timeout_increase(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        sleep_tag = AdHocTag(Path("/usr/bin/sleep"))
        sleep_tag.configure("1s", timeout_ms=2000)

        result = sleep_tag.process(hello_file, "")

        assert result == ""

    def test_executable_explicit_timeout_exceeded(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        sleep_tag = AdHocTag(Path("/usr/bin/sleep"))
        sleep_tag.configure("3s", timeout_ms=2000)

        with pytest.raises(ExecutionTimeoutError) as exc:
            sleep_tag.process(hello_file, "")

        assert exc.match("timeout")
