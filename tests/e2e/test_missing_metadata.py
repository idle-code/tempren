import io
import shutil
from pathlib import Path

import pytest

from .conftest import CliTestsBase, ErrorCode, run_tempren

image_path = Path(__file__).parent.parent / "test_data" / "image" / "photo.jpg"
template = "%Image.Width()_%Name()"


@pytest.fixture
def mixed_data_dir(text_data_dir: Path) -> Path:
    """Directory with text files (no image width) and a single image"""
    shutil.copy(image_path, text_data_dir)
    return text_data_dir


class TestMissingMetadata(CliTestsBase):
    @pytest.mark.parametrize("flag", ["-ms", "--missing-stop", None])
    def test_stop(self, mixed_data_dir: Path, flag: str | None):
        stdout, stderr, error_code = run_tempren(
            flag, "--sort", "%Name()", template, mixed_data_dir
        )

        assert error_code == ErrorCode.MISSING_METADATA_ERROR
        assert "%Image.Width() has no value for 'hello.txt'" in stderr
        assert stderr.count("has no value") == 1
        assert sorted(p.name for p in mixed_data_dir.iterdir()) == [
            "hello.txt",
            "markdown.md",
            "photo.jpg",
        ]

    @pytest.mark.parametrize("flag", ["-mi", "--missing-ignore"])
    def test_ignore(self, mixed_data_dir: Path, flag: str):
        stdout, stderr, error_code = run_tempren(flag, template, mixed_data_dir)

        assert error_code == ErrorCode.SUCCESS
        assert sorted(p.name for p in mixed_data_dir.iterdir()) == [
            "1008_photo.jpg",
            "_hello.txt",
            "_markdown.md",
        ]

    @pytest.mark.parametrize("flag", ["-mk", "--missing-skip"])
    def test_skip(self, mixed_data_dir: Path, flag: str):
        stdout, stderr, error_code = run_tempren(flag, template, mixed_data_dir)

        assert error_code == ErrorCode.SUCCESS
        assert "Skipping: %Image.Width() has no value for 'hello.txt'" in stderr
        assert sorted(p.name for p in mixed_data_dir.iterdir()) == [
            "1008_photo.jpg",
            "hello.txt",
            "markdown.md",
        ]

    def test_flags_are_mutually_exclusive(self, mixed_data_dir: Path):
        stdout, stderr, error_code = run_tempren("-mi", "-mk", template, mixed_data_dir)

        assert error_code == ErrorCode.USAGE_ERROR

    @pytest.mark.parametrize(
        "answers, expected_names",
        [
            ("", ["1008_photo.jpg", "_hello.txt", "_markdown.md"]),
            ("k\nskip\n", ["1008_photo.jpg", "hello.txt", "markdown.md"]),
            ("c\nA\ncustom\nB\n", ["1008_photo.jpg", "A_hello.txt", "B_markdown.md"]),
            ("invalid\ni\ni\n", ["1008_photo.jpg", "_hello.txt", "_markdown.md"]),
        ],
    )
    def test_manual(
        self, mixed_data_dir: Path, monkeypatch, answers: str, expected_names: list
    ):
        monkeypatch.setattr("sys.stdin", io.StringIO(answers + "\n" * 4))

        stdout, stderr, error_code = run_tempren(
            "--missing-manual", "--sort", "%Name()", template, mixed_data_dir
        )

        assert error_code == ErrorCode.SUCCESS
        assert "following tag could not produce a value" in stderr
        assert sorted(p.name for p in mixed_data_dir.iterdir()) == expected_names

    def test_manual_stop(self, mixed_data_dir: Path, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("s\n"))

        stdout, stderr, error_code = run_tempren(
            "--missing-manual", "--sort", "%Name()", template, mixed_data_dir
        )

        assert error_code == ErrorCode.MISSING_METADATA_ERROR

    def test_skip_while_filtering(self, mixed_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            "--missing-skip",
            "--filter-template",
            "%Image.Width() > 1000",
            "%Upper(){%Name()}",
            mixed_data_dir,
        )

        assert error_code == ErrorCode.SUCCESS
        assert sorted(p.name for p in mixed_data_dir.iterdir()) == [
            "PHOTO.JPG",
            "hello.txt",
            "markdown.md",
        ]

    def test_failing_adhoc_tag_stops_by_default(self, text_data_dir: Path):
        stdout, stderr, error_code = run_tempren(
            "--ad-hoc", "Fail=false", "%Fail()_%Name()", text_data_dir
        )

        assert error_code == ErrorCode.MISSING_METADATA_ERROR
        assert "%Fail() has no value for" in stderr
