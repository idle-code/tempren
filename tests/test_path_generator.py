from pathlib import Path

import pytest

from tempren.primitives import File


class TestFile:
    def test_input_directory_have_to_be_absolute(self):
        input_directory = Path("relative")
        file_path = Path("path")

        with pytest.raises(AssertionError):
            File(input_directory, file_path)

    def test_file_path_have_to_be_relative(self):
        input_directory = Path("/absolute")
        file_path = Path("/absolute/path")

        with pytest.raises(AssertionError):
            File(input_directory, file_path)

    def test_absolute_path(self):
        input_directory = Path("/absolute/subdirectory")
        file_path = Path("file/path")

        absolute_path = File(input_directory, file_path).absolute_path

        assert absolute_path == Path("/absolute/subdirectory/file/path")

    def test_from_single_string_path(self):
        file_path = "/absolute/subdirectory/file/path"

        file = File.from_path(file_path)

        assert file.input_directory == Path("/absolute/subdirectory/file")
        assert file.absolute_path == Path("/absolute/subdirectory/file/path")
        assert file.relative_path == Path("path")
