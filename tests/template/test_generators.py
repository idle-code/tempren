import os
from pathlib import Path

import pytest

from tempren.primitives import File
from tempren.template.ast import PatternElementSequence, RawText
from tempren.template.exceptions import InvalidFilenameError
from tempren.template.generators import TemplateNameGenerator, TemplatePathGenerator


def static_pattern(text: str) -> PatternElementSequence:
    return PatternElementSequence([RawText(text)])


class TestTemplateNameGenerator:
    def test_replacement_is_used_for_filename(self, text_data_dir: Path):
        generator = TemplateNameGenerator(static_pattern("new_name"))
        os.chdir(text_data_dir)
        src_file = File(text_data_dir, Path("hello.txt"))

        dst_path = generator.generate(src_file)

        assert dst_path.parent == src_file.relative_path.parent
        assert dst_path.name == "new_name"

    def test_generated_replacement_is_path(self, text_data_dir: Path):
        generator = TemplateNameGenerator(static_pattern("file/path"))
        os.chdir(text_data_dir)
        src_file = File(text_data_dir, Path("hello.txt"))

        with pytest.raises(InvalidFilenameError) as exc:
            generator.generate(src_file)

        assert exc.match("file/path")


class TestTemplatePathGenerator:
    def test_replacement_is_used_for_path(self, text_data_dir: Path):
        generator = TemplatePathGenerator(static_pattern("new/file/path"))
        os.chdir(text_data_dir)
        src_file = File(text_data_dir, Path("hello.txt"))

        dst_path = generator.generate(src_file)

        assert dst_path == Path("new/file/path")
