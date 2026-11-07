from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tempren.exceptions import MetadataUnavailableError, MissingMetadataError
from tempren.frontend import NullFrontend, SkipReason
from tempren.pipeline import (
    ConflictResolutionStrategy,
    FilterType,
    MissingMetadataStrategy,
    RuntimeConfiguration,
    build_pipeline,
    build_tag_registry,
)
from tempren.primitives import CategoryName, File, Tag
from tempren.template.registry import TagRegistry


class HelloOnlyTag(Tag):
    """Has value only for 'hello.txt' file"""

    require_context = False

    def process(self, file: File, context: str | None) -> str:
        if file.relative_path.name == "hello.txt":
            return "HELLO"
        raise MissingMetadataError("No hello here")


@dataclass
class RecordingFrontend:
    conflict_resolution: ConflictResolutionStrategy | Path = (
        ConflictResolutionStrategy.stop
    )
    missing_metadata_resolution: MissingMetadataStrategy | str = (
        MissingMetadataStrategy.stop
    )
    events: list[tuple] = field(default_factory=list)
    errors: list[MetadataUnavailableError] = field(default_factory=list)

    def resolve_conflict(
        self, source: File, destination: Path
    ) -> ConflictResolutionStrategy | Path:
        self.events.append(("conflict", str(source), destination))
        return self.conflict_resolution

    def resolve_missing_metadata(
        self, error: MetadataUnavailableError
    ) -> MissingMetadataStrategy | str:
        self.events.append(("missing", str(error.file), str(error.tag_name)))
        return self.missing_metadata_resolution

    def files_gathered(self, count: int) -> None:
        self.events.append(("gathered", count))

    def file_renamed(self, source: File, destination: Path, overridden: bool) -> None:
        self.events.append(("renamed", str(source), destination, overridden))

    def file_skipped(
        self,
        source: File,
        destination: Path | None,
        reason: SkipReason,
        error: MetadataUnavailableError | None = None,
    ) -> None:
        self.events.append(("skipped", str(source), destination, reason))
        if error:
            self.errors.append(error)


@pytest.fixture(scope="module")
def registry() -> TagRegistry:
    registry = build_tag_registry({}, {})
    registry.register_category(CategoryName("Test")).register_tag_class(HelloOnlyTag)
    return registry


def run_pipeline(registry: TagRegistry, frontend, **config_args) -> None:
    config_args.setdefault("sort", "%Name()")
    config = RuntimeConfiguration(**config_args)
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


class TestPipelineMissingMetadata:
    template = "%Test.HelloOnly()_%Name()"

    def run(
        self,
        registry: TagRegistry,
        text_data_dir: Path,
        strategy: MissingMetadataStrategy,
        frontend: RecordingFrontend | None = None,
        **config_args,
    ) -> RecordingFrontend:
        frontend = frontend or RecordingFrontend()
        config_args.setdefault("template", self.template)
        run_pipeline(
            registry,
            frontend,
            input_paths=[text_data_dir],
            missing_metadata_strategy=strategy,
            **config_args,
        )
        return frontend

    def test_stop_is_the_default(self):
        config = RuntimeConfiguration(template="", input_paths=[])

        assert config.missing_metadata_strategy == MissingMetadataStrategy.stop

    def test_stop_raises_error_describing_the_cause(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        with pytest.raises(MetadataUnavailableError) as exc:
            self.run(registry, text_data_dir, MissingMetadataStrategy.stop)

        assert str(exc.value.file) == "markdown.md"
        assert str(exc.value.tag_name) == "Test.HelloOnly"
        assert exc.value.reason == "No hello here"
        assert isinstance(exc.value.__cause__, MissingMetadataError)
        assert (text_data_dir / "markdown.md").exists()

    def test_ignore_renders_empty_string(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        self.run(registry, text_data_dir, MissingMetadataStrategy.ignore)

        assert sorted(p.name for p in text_data_dir.iterdir()) == [
            "HELLO_hello.txt",
            "_markdown.md",
        ]

    def test_skip_leaves_file_intact(self, registry: TagRegistry, text_data_dir: Path):
        frontend = self.run(registry, text_data_dir, MissingMetadataStrategy.skip)

        assert frontend.events == [
            ("gathered", 2),
            ("renamed", "hello.txt", Path("HELLO_hello.txt"), False),
            ("skipped", "markdown.md", None, SkipReason.missing_metadata),
        ]
        assert str(frontend.errors[0].tag_name) == "Test.HelloOnly"
        assert (text_data_dir / "markdown.md").exists()

    def test_skip_in_filtering_excludes_the_file(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = self.run(
            registry,
            text_data_dir,
            MissingMetadataStrategy.skip,
            template="%Upper(){%Name()}",
            filter_type=FilterType.template,
            filter="%Test.HelloOnly() == 'HELLO'",
        )

        assert frontend.events == [
            ("skipped", "markdown.md", None, SkipReason.missing_metadata),
            ("gathered", 1),
            ("renamed", "hello.txt", Path("HELLO.TXT"), False),
        ]

    def test_skipped_file_is_not_included_by_inverted_filter(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = self.run(
            registry,
            text_data_dir,
            MissingMetadataStrategy.skip,
            template="%Upper(){%Name()}",
            filter_type=FilterType.template,
            filter="%Test.HelloOnly() == 'HELLO'",
            filter_invert=True,
        )

        assert ("gathered", 0) in frontend.events

    def test_skip_in_sorting_excludes_the_file(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = self.run(
            registry,
            text_data_dir,
            MissingMetadataStrategy.skip,
            template="%Upper(){%Name()}",
            sort="%Test.HelloOnly()",
        )

        assert frontend.events == [
            ("gathered", 2),
            ("skipped", "markdown.md", None, SkipReason.missing_metadata),
            ("renamed", "hello.txt", Path("HELLO.TXT"), False),
        ]

    def test_stop_in_filtering_raises_error(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        with pytest.raises(MetadataUnavailableError):
            self.run(
                registry,
                text_data_dir,
                MissingMetadataStrategy.stop,
                template="%Name()",
                filter_type=FilterType.template,
                filter="%Test.HelloOnly() == 'HELLO'",
            )

    def test_manual_custom_value_is_used_as_tag_value(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = RecordingFrontend(missing_metadata_resolution="CUSTOM")

        self.run(registry, text_data_dir, MissingMetadataStrategy.manual, frontend)

        assert ("missing", "markdown.md", "Test.HelloOnly") in frontend.events
        assert (text_data_dir / "CUSTOM_markdown.md").exists()

    def test_manual_selected_strategy_is_applied(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = RecordingFrontend(
            missing_metadata_resolution=MissingMetadataStrategy.skip
        )

        self.run(registry, text_data_dir, MissingMetadataStrategy.manual, frontend)

        assert frontend.events[-1] == (
            "skipped",
            "markdown.md",
            None,
            SkipReason.missing_metadata,
        )

    def test_manual_cannot_select_manual_again(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        frontend = RecordingFrontend(
            missing_metadata_resolution=MissingMetadataStrategy.manual
        )

        with pytest.raises(ValueError):
            self.run(registry, text_data_dir, MissingMetadataStrategy.manual, frontend)

    def test_null_frontend_does_not_support_manual_resolution(
        self, registry: TagRegistry, text_data_dir: Path
    ):
        with pytest.raises(NotImplementedError):
            self.run(
                registry,
                text_data_dir,
                MissingMetadataStrategy.manual,
                NullFrontend(),  # type: ignore[arg-type]
            )
