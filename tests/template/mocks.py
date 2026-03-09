from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from tempren.primitives import File, Tag
from tempren.template.parser import ArgValue


@dataclass
class MockTag(Tag):
    args: tuple[ArgValue, ...] = ()
    kwargs: Mapping[str, ArgValue] = field(default_factory=dict)
    file: File | None = None
    context: str | None = None
    process_output: Any = "Mock output"
    configure_invoked: bool = False
    process_invoked: bool = False
    require_context: bool | None = None

    def configure(self, *args, **kwargs):
        self.configure_invoked = True
        self.args = args
        self.kwargs = kwargs

    def process(self, file: File, context: str | None) -> Any:
        self.process_invoked = True
        self.file = file
        self.context = context
        return self.process_output


@dataclass
class GeneratorTag(Tag):
    output_generator: Callable[[File, str | None], Any]

    def process(self, file: File, context: str | None) -> Any:
        return self.output_generator(file, context)
