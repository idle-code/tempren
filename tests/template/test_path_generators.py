from pathlib import Path

import pytest

from tempren.pipeline import File
from tempren.template.path_generators import (
    TemplateNameGenerator,
    TemplatePathGenerator,
)
from tempren.template.tree_elements import Pattern, RawText


def static_pattern(text: str) -> Pattern:
    return Pattern([RawText(text)])


class TestTemplateNameGenerator:
    def test_replacement_is_used_for_filename(self):
        generator = TemplateNameGenerator(static_pattern("new_name"))
        src_file = File(Path("path/to/file"))

        dst_path = generator.generate(src_file)

        assert dst_path.parent == src_file.path.parent
        assert dst_path.name == "new_name"

    def test_generated_replacement_is_path(self):
        generator = TemplateNameGenerator(static_pattern("file/path"))
        src_file = File(Path("path/to/file"))

        with pytest.raises(ValueError) as exc:
            generator.generate(src_file)

        assert exc.match("file/path")


class TestTemplatePathGenerator:
    def test_replacement_is_used_for_path(self):
        generator = TemplatePathGenerator(static_pattern("new/file/path"))
        src_file = File(Path("path/to/file"))

        dst_path = generator.generate(src_file)

        assert dst_path == Path("new/file/path")
