import os
from pathlib import Path
from typing import Callable

import pytest
from tempren.filesystem import FileGatherer, Renamer


@pytest.fixture
def nested_data_dir(test_data_dir: Callable[[str], Path]) -> Path:
    yield from test_data_dir("nested")


@pytest.fixture
def hidden_data_dir(test_data_dir: Callable[[str], Path]) -> Path:
    yield from test_data_dir("hidden")


class TestFileGatherer:
    def test_empty_directory(self, tmp_path: Path):
        gatherer = FileGatherer(tmp_path)
        file_iterator = iter(gatherer)

        with pytest.raises(StopIteration):
            next(file_iterator)

    def test_flat_directory(self, text_data_dir: Path):
        gatherer = FileGatherer(text_data_dir)

        files = set(gatherer)

        test_files = {text_data_dir / "hello.txt", text_data_dir / "markdown.md"}
        assert files == test_files

    def test_nested_files(self, nested_data_dir: Path):
        gatherer = FileGatherer(nested_data_dir)

        files = set(gatherer)

        test_files = {
            nested_data_dir / "level-1.file",
            nested_data_dir / "first" / "level-2.file",
            nested_data_dir / "second" / "level-2.file",
            nested_data_dir / "second" / "third" / "level-3.file",
        }
        assert files == test_files

    def test_hidden_files_are_skipped_by_default(self, hidden_data_dir: Path):
        gatherer = FileGatherer(hidden_data_dir)

        files = set(gatherer)

        test_files = {
            hidden_data_dir / "visible.txt",
        }
        assert files == test_files


class TestRenamer:
    def test_rename_same_name(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        dst = text_data_dir / "hi.txt"
        assert not dst.exists()
        renamer = Renamer()

        renamer(src, dst)

        assert dst.exists()
