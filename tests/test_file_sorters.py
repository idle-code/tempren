from pathlib import Path

import pytest

from tempren.file_sorters import TemplateFileSorter
from tempren.path_generator import File
from tempren.template.tree_elements import Pattern, RawText, TagInstance

from .template.mocks import GeneratorTag, MockTag


class TestTemplateFileSorter:
    @pytest.mark.parametrize("expression_text", ["", "$%", "1 +", "while True: pass"])
    def test_invalid_expression(self, expression_text: str):
        pattern = Pattern([RawText(expression_text)])
        file_sorter = TemplateFileSorter(pattern)
        file = File(Path("some/file.name"))

        with pytest.raises(SyntaxError):
            file_sorter([file])

    @pytest.mark.parametrize(
        "expression_text,expected_result",
        [
            ("True, False", (True, False)),
            ("123", (0,)),
            ("'foo', 'bar'", ("foo", "bar")),
            ("''", ("",)),
        ],
    )
    def test_valid_expression(self, expression_text: str, expected_result: bool):
        filepath_tag = GeneratorTag(lambda path, context: str(path))
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
