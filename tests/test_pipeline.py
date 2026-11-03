from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tempren.frontend import NullFrontend, SkipReason
from tempren.pipeline import (
    ConflictResolutionStrategy,
    RuntimeConfiguration,
    build_pipeline,
    build_tag_registry,
)
from tempren.primitives import File
from tempren.template.registry import TagRegistry


@dataclass
class RecordingFrontend:
    conflict_resolution: ConflictResolutionStrategy | Path = (
        ConflictResolutionStrategy.stop
    )
    events: list[tuple] = field(default_factory=list)

    def resolve_conflict(
        self, source: File, destination: Path
    ) -> ConflictResolutionStrategy | Path:
        self.events.append(("conflict", str(source), destination))
        return self.conflict_resolution

    def files_gathered(self, count: int) -> None:
        self.events.append(("gathered", count))

    def file_renamed(self, source: File, destination: Path, overridden: bool) -> None:
        self.events.append(("renamed", str(source), destination, overridden))

    def file_skipped(self, source: File, destination: Path, reason: SkipReason) -> None:
        self.events.append(("skipped", str(source), destination, reason))


@pytest.fixture(scope="module")
def registry() -> TagRegistry:
    return build_tag_registry({}, {})


def run_pipeline(registry: TagRegistry, frontend, **config_args) -> None:
    config = RuntimeConfiguration(sort="%Name()", **config_args)
    build_pipeline(config, registry, frontend).execute()


class TestPipelineFrontendNotifications:
    def test_renamed_files_are_reported_in_order(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = RecordingFrontend()

        run_pipeline(
            registry,
            frontend,
            template="%Upper(){%Name()}",
            input_paths=[text_data_dir],
        )

        assert frontend.events == [
            ("gathered", 2),
            ("renamed", "hello.txt", Path("HELLO.TXT"), False),
            ("renamed", "markdown.md", Path("MARKDOWN.MD"), False),
        ]
        assert (text_data_dir / "HELLO.TXT").exists()

    def test_dry_run_reports_renames_without_changes(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = RecordingFrontend()

        run_pipeline(
            registry,
            frontend,
            template="%Upper(){%Name()}",
            input_paths=[text_data_dir],
            dry_run=True,
        )

        assert ("renamed", "hello.txt", Path("HELLO.TXT"), False) in frontend.events
        assert (text_data_dir / "hello.txt").exists()
        assert not (text_data_dir / "HELLO.TXT").exists()

    def test_same_path_is_reported_as_skipped(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = RecordingFrontend()

        run_pipeline(
            registry, frontend, template="%Name()", input_paths=[text_data_dir]
        )

        assert frontend.events == [
            ("gathered", 2),
            ("skipped", "hello.txt", Path("hello.txt"), SkipReason.same_path),
            ("skipped", "markdown.md", Path("markdown.md"), SkipReason.same_path),
        ]

    def test_ignored_conflict_is_reported_as_skipped(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = RecordingFrontend()

        run_pipeline(
            registry,
            frontend,
            template="StaticFilename",
            input_paths=[text_data_dir],
            conflict_strategy=ConflictResolutionStrategy.ignore,
        )

        assert frontend.events == [
            ("gathered", 2),
            ("renamed", "hello.txt", Path("StaticFilename"), False),
            (
                "skipped",
                "markdown.md",
                Path("StaticFilename"),
                SkipReason.conflict_ignored,
            ),
        ]


class TestPipelineManualConflictResolution:
    def run_with_conflict(
        self,
        registry: TagRegistry,
        text_data_dir: Path,
        resolution: ConflictResolutionStrategy | Path,
    ) -> RecordingFrontend:
        frontend = RecordingFrontend(conflict_resolution=resolution)
        run_pipeline(
            registry,
            frontend,
            template="StaticFilename",
            input_paths=[text_data_dir],
            conflict_strategy=ConflictResolutionStrategy.manual,
        )
        assert ("conflict", "markdown.md", Path("StaticFilename")) in frontend.events
        return frontend

    def test_custom_path_is_relative_to_input_directory(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = self.run_with_conflict(
            registry, text_data_dir, Path("UserProvidedName")
        )

        assert frontend.events[-1] == (
            "renamed",
            "markdown.md",
            Path("UserProvidedName"),
            False,
        )
        assert (text_data_dir / "StaticFilename").exists()
        assert (text_data_dir / "UserProvidedName").exists()

    def test_override_is_reported(self, registry: TagRegistry, text_data_dir: Path):
        frontend = self.run_with_conflict(
            registry, text_data_dir, ConflictResolutionStrategy.override
        )

        assert frontend.events[-1] == (
            "renamed",
            "markdown.md",
            Path("StaticFilename"),
            True,
        )
        assert sorted(p.name for p in text_data_dir.iterdir()) == ["StaticFilename"]

    def test_null_frontend_does_not_support_manual_resolution(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        with pytest.raises(NotImplementedError):
            run_pipeline(
                registry,
                NullFrontend(),
                template="StaticFilename",
                input_paths=[text_data_dir],
                conflict_strategy=ConflictResolutionStrategy.manual,
            )


def test_rebuilt_pipeline_starts_with_fresh_tag_state(
    registry: TagRegistry, text_data_dir: Path
):
    """Dry-run preview followed by an actual run should generate the same names"""
    preview_frontend = RecordingFrontend()
    run_pipeline(
        registry,
        preview_frontend,
        template="%Count()%Ext()",
        input_paths=[text_data_dir],
        dry_run=True,
    )
    apply_frontend = RecordingFrontend()

    run_pipeline(
        registry,
        apply_frontend,
        template="%Count()%Ext()",
        input_paths=[text_data_dir],
    )

    assert preview_frontend.events == apply_frontend.events
    assert sorted(p.name for p in text_data_dir.iterdir()) == ["0.txt", "1.md"]
