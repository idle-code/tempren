import os
from pathlib import Path
from typing import Callable

import pytest

from tempren.filesystem import FileGatherer, FileMover, FileRenamer, PrintingOnlyRenamer


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


class TestFileRenamer:
    def test_same_name(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        renamer = FileRenamer()

        renamer(src, src)

        assert src.exists()

    def test_simple_file(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        assert src.is_file()
        dst = text_data_dir / "hi.txt"
        assert not dst.exists()
        renamer = FileRenamer()

        renamer(src, dst)

        assert dst.exists()

    def test_simple_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "first"
        assert src.is_dir()
        dst = nested_data_dir / "fourth"
        assert not dst.exists()
        renamer = FileRenamer()

        renamer(src, dst)

        assert dst.exists()

    def test_source_doesnt_exists(self, text_data_dir: Path):
        src = text_data_dir / "goodbye.txt"
        assert not src.exists()
        dst = text_data_dir / "bye.md"
        renamer = FileRenamer()

        with pytest.raises(FileNotFoundError) as exc:
            renamer(src, dst)
        assert exc.match(str(src))

    def test_destination_file_exists(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        dst = text_data_dir / "markdown.md"
        assert dst.exists()
        renamer = FileRenamer()

        with pytest.raises(FileExistsError) as exc:
            renamer(src, dst)
        assert exc.match(str(dst))

    def test_destination_is_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "level-1.file"
        dst = nested_data_dir / "first"
        assert dst.is_dir()
        renamer = FileRenamer()

        with pytest.raises(FileExistsError) as exc:
            renamer(src, dst)
        assert exc.match(str(dst))


class TestFileMover:
    def test_same_name(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        mover = FileMover()

        mover(src, src)

        assert src.exists()

    def test_simple_file(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        assert src.is_file()
        dst = text_data_dir / "hi.txt"
        assert not dst.exists()
        mover = FileMover()

        mover(src, dst)

        assert dst.exists()
        assert not src.exists()

    def test_source_doesnt_exists(self, text_data_dir: Path):
        src = text_data_dir / "goodbye.txt"
        assert not src.exists()
        dst = text_data_dir / "bye.md"
        mover = FileMover()

        with pytest.raises(FileNotFoundError) as exc:
            mover(src, dst)
        assert exc.match(str(src))

    def test_destination_file_exists(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        dst = text_data_dir / "markdown.md"
        assert dst.exists()
        mover = FileMover()

        with pytest.raises(FileExistsError) as exc:
            mover(src, dst)
        assert exc.match(str(dst))

    def test_destination_is_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "level-1.file"
        dst = nested_data_dir / "first"
        assert dst.is_dir()
        mover = FileMover()

        with pytest.raises(FileExistsError) as exc:
            mover(src, dst)
        assert exc.match(str(dst))

    def test_create_single_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "level-1.file"
        nonexistent_dir = nested_data_dir / "nonexistent"
        dst = nonexistent_dir / "level-1.file"
        assert not nonexistent_dir.exists()
        mover = FileMover()

        mover(src, dst)

        assert nonexistent_dir.exists()
        assert dst.exists()

    def test_create_path_part_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "second" / "level-2.file"
        nonexistent_dir = nested_data_dir / "second" / "nonexistent"
        dst = nonexistent_dir / "level-2.file"
        assert not nonexistent_dir.exists()
        mover = FileMover()

        mover(src, dst)

        assert nonexistent_dir.exists()
        assert dst.exists()

    def test_create_multiple_directories(self, nested_data_dir: Path):
        src = nested_data_dir / "level-1.file"
        nonexistent_dir = nested_data_dir / "a" / "b" / "c"
        dst = nonexistent_dir / "level-1.file"
        assert not nonexistent_dir.exists()
        mover = FileMover()

        mover(src, dst)

        assert nonexistent_dir.exists()
        assert dst.exists()

    def test_create_already_existing_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "level-1.file"
        existing_dir = nested_data_dir / "second"
        dst = existing_dir / "level-1.file"
        assert existing_dir.exists()
        mover = FileMover()

        mover(src, dst)

        assert existing_dir.exists()
        assert dst.exists()


class TestPrintingOnlyRenamer:
    def test_same_name(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        renamer = PrintingOnlyRenamer()

        renamer(src, src)

        assert src.exists()

    def test_simple_file(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        assert src.is_file()
        dst = text_data_dir / "hi.txt"
        assert not dst.exists()
        renamer = PrintingOnlyRenamer()

        renamer(src, dst)

        assert not dst.exists()

    def test_simple_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "first"
        assert src.is_dir()
        dst = nested_data_dir / "fourth"
        assert not dst.exists()
        renamer = PrintingOnlyRenamer()

        renamer(src, dst)

        assert not dst.exists()

    def test_source_doesnt_exists(self, text_data_dir: Path):
        src = text_data_dir / "goodbye.txt"
        assert not src.exists()
        dst = text_data_dir / "bye.md"
        renamer = PrintingOnlyRenamer()

        with pytest.raises(FileNotFoundError) as exc:
            renamer(src, dst)
        assert exc.match(str(src))

    def test_destination_file_exists(self, text_data_dir: Path):
        src = text_data_dir / "hello.txt"
        dst = text_data_dir / "markdown.md"
        assert dst.exists()
        renamer = PrintingOnlyRenamer()

        with pytest.raises(FileExistsError) as exc:
            renamer(src, dst)
        assert exc.match(str(dst))

    def test_destination_is_directory(self, nested_data_dir: Path):
        src = nested_data_dir / "level-1.file"
        dst = nested_data_dir / "first"
        assert dst.is_dir()
        renamer = PrintingOnlyRenamer()

        with pytest.raises(FileExistsError) as exc:
            renamer(src, dst)
        assert exc.match(str(dst))
