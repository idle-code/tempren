from pathlib import Path

import pytest

from tempren.file_sorters import TemplateFileSorter
from tempren.path_generator import File
from tempren.template.tree_elements import Pattern, RawText, TagInstance

from .template.mocks import GeneratorTag


class TestTemplateFileSorter:
    @pytest.mark.parametrize("expression_text", ["", "$%", "1 +", "while True: pass"])
    def test_invalid_expression(self, expression_text: str, nonexistent_path: Path):
        pattern = Pattern([RawText(expression_text)])
        file_sorter = TemplateFileSorter(pattern)
        file = File(nonexistent_path)

        with pytest.raises(SyntaxError):
            file_sorter([file])

    @pytest.mark.parametrize(
        "tag_implementation",
        [
            lambda path, context: path,
            lambda path, context: str(path),
            lambda path, context: int(str(path)),
            lambda path, context: ("constant", str(path), int(str(path))),
        ],
    )
    def test_single_tag_output(self, tag_implementation):
        filepath_tag = GeneratorTag(
            lambda path, context: tag_implementation(path, context)
        )
        pattern = Pattern([TagInstance(tag=filepath_tag)])
        file_sorter = TemplateFileSorter(pattern)
        files = [
            File(Path("3")),
            File(Path("1")),
            File(Path("2")),
        ]

        sorted_files = file_sorter(files)

        assert sorted_files == [
            File(Path("1")),
            File(Path("2")),
            File(Path("3")),
        ]

    @pytest.mark.parametrize(
        "tag1_implementation,tag2_implementation",
        [
            (lambda path, context: path, lambda path, context: "constant"),
            (lambda path, context: "constant", lambda path, context: path),
            (lambda path, context: int(str(path)), lambda path, context: str(path)),
        ],
    )
    def test_multiple_tag_output(self, tag1_implementation, tag2_implementation):
        filepath_tag1 = GeneratorTag(
            lambda path, context: tag1_implementation(path, context)
        )
        filepath_tag2 = GeneratorTag(
            lambda path, context: tag2_implementation(path, context)
        )
        pattern = Pattern(
            [
                TagInstance(tag=filepath_tag1),
                RawText(", "),
                TagInstance(tag=filepath_tag2),
            ]
        )
        file_sorter = TemplateFileSorter(pattern)
        files = [
            File(Path("3")),
            File(Path("1")),
            File(Path("2")),
        ]

        sorted_files = file_sorter(files)

        assert sorted_files == [
            File(Path("1")),
            File(Path("2")),
            File(Path("3")),
        ]
