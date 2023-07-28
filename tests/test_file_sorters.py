from pathlib import Path

import pytest

from tempren.exceptions import TemplateEvaluationError
from tempren.file_sorters import TemplateFileSorter
from tempren.primitives import File
from tempren.template.ast import PatternElementSequence, RawText, TagInstance

from .template.mocks import GeneratorTag


class TestTemplateFileSorter:
    @pytest.mark.parametrize("expression_text", ["", "$%", "1 +", "while True: pass"])
    def test_invalid_expression(self, expression_text: str, nonexistent_file: File):
        pattern = PatternElementSequence([RawText(expression_text)])
        pattern.source_representation = expression_text
        file_sorter = TemplateFileSorter(pattern)

        with pytest.raises(TemplateEvaluationError):
            file_sorter([nonexistent_file])

    @pytest.mark.parametrize(
        "tag_implementation",
        [
            lambda file, context: file.relative_path,
            lambda file, context: str(file.relative_path),
            lambda file, context: int(str(file.relative_path)),
            lambda file, context: (
                "constant",
                str(file.relative_path),
                int(str(file.relative_path)),
            ),
        ],
    )
    def test_single_tag_output(
        self, tag_implementation, nonexistent_absolute_path: Path
    ):
        filepath_tag = GeneratorTag(tag_implementation)
        pattern = PatternElementSequence([TagInstance(tag=filepath_tag)])
        file_sorter = TemplateFileSorter(pattern)
        files = [
            File(nonexistent_absolute_path, Path("3")),
            File(nonexistent_absolute_path, Path("1")),
            File(nonexistent_absolute_path, Path("2")),
        ]

        sorted_files = file_sorter(files)

        assert sorted_files == [
            File(nonexistent_absolute_path, Path("1")),
            File(nonexistent_absolute_path, Path("2")),
            File(nonexistent_absolute_path, Path("3")),
        ]

    @pytest.mark.parametrize(
        "tag1_implementation,tag2_implementation",
        [
            (
                lambda file, context: "constant",
                lambda file, context: str(file.relative_path),
            ),
            (
                lambda file, context: int(str(file.relative_path)),
                lambda file, context: str(file.relative_path),
            ),
        ],
    )
    def test_tag_output_rendering(
        self, tag1_implementation, tag2_implementation, nonexistent_absolute_path: Path
    ):
        tag1 = GeneratorTag(tag1_implementation)
        tag2 = GeneratorTag(tag2_implementation)
        pattern = PatternElementSequence(
            [
                TagInstance(tag=tag1),
                RawText(", "),
                TagInstance(tag=tag2),
            ]
        )
        file_sorter = TemplateFileSorter(pattern)
        files = [
            File(nonexistent_absolute_path, Path("3")),
            File(nonexistent_absolute_path, Path("1")),
            File(nonexistent_absolute_path, Path("2")),
        ]

        sorted_files = file_sorter(files)

        assert sorted_files == [
            File(nonexistent_absolute_path, Path("1")),
            File(nonexistent_absolute_path, Path("2")),
            File(nonexistent_absolute_path, Path("3")),
        ]

    def test_path_rendering(self, nonexistent_absolute_path: Path):
        filepath_tag = GeneratorTag(lambda file, context: file.relative_path)
        pattern = PatternElementSequence([TagInstance(tag=filepath_tag)])
        file_sorter = TemplateFileSorter(pattern)
        files = [
            File(nonexistent_absolute_path, Path("3")),
            File(nonexistent_absolute_path, Path("1")),
            File(nonexistent_absolute_path, Path("2")),
        ]

        sorted_files = file_sorter(files)

        assert sorted_files == [
            File(nonexistent_absolute_path, Path("1")),
            File(nonexistent_absolute_path, Path("2")),
            File(nonexistent_absolute_path, Path("3")),
        ]
