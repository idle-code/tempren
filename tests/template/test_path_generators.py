from pathlib import Path

import pytest

from tempren.path_generator import File
from tempren.template.path_generators import (
    TemplateNameGenerator,
    TemplatePathGenerator,
)
from tempren.template.tree_elements import Pattern, RawText


def static_pattern(text: str) -> Pattern:
    return Pattern([RawText(text)])


class TestTemplateNameGenerator:
    def test_replacement_is_used_for_filename(self, text_data_dir: Path):
        generator = TemplateNameGenerator(text_data_dir, static_pattern("new_name"))
        src_file = File(text_data_dir / "hello.txt")

        dst_path = generator.generate(src_file)

        assert dst_path.parent == src_file.path.parent
        assert dst_path.name == "new_name"

    def test_generated_replacement_is_path(self, text_data_dir: Path):
        generator = TemplateNameGenerator(text_data_dir, static_pattern("file/path"))
        src_file = File(text_data_dir / "hello.txt")

        with pytest.raises(ValueError) as exc:
            generator.generate(src_file)

        assert exc.match("file/path")


class TestTemplatePathGenerator:
    def test_replacement_is_used_for_path(self, text_data_dir: Path):
        generator = TemplatePathGenerator(
            text_data_dir, static_pattern("new/file/path")
        )
        src_file = File(text_data_dir / "hello.txt")

        dst_path = generator.generate(src_file)

        assert dst_path == Path("new/file/path")
