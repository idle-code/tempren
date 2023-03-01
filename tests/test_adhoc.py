from pathlib import Path

import pytest

from tempren.adhoc import AdHocTag
from tempren.exceptions import ExecutionTimeoutError, MissingMetadataError
from tempren.primitives import File


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

    @pytest.mark.slow
    def test_executable_default_timeout(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        sleep_tag = AdHocTag(Path("/usr/bin/sleep"))
        sleep_tag.configure("4s")

        with pytest.raises(ExecutionTimeoutError) as exc:
            sleep_tag.process(hello_file, "")

        assert exc.match("timeout")

    @pytest.mark.slow
    def test_executable_explicit_timeout_increase(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        sleep_tag = AdHocTag(Path("/usr/bin/sleep"))
        sleep_tag.configure("1s", timeout_ms=2000)

        result = sleep_tag.process(hello_file, "")

        assert result == ""

    @pytest.mark.slow
    def test_executable_explicit_timeout_exceeded(self, text_data_dir: Path):
        hello_file = File(text_data_dir, Path("hello.txt"))
        sleep_tag = AdHocTag(Path("/usr/bin/sleep"))
        sleep_tag.configure("3s", timeout_ms=2000)

        with pytest.raises(ExecutionTimeoutError) as exc:
            sleep_tag.process(hello_file, "")

        assert exc.match("timeout")
