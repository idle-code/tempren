from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Tuple

from tempren.path_generator import File
from tempren.template.tree_builder import ArgValue
from tempren.template.tree_elements import Tag


@dataclass
class MockTag(Tag):
    args: Tuple[ArgValue, ...] = ()
    kwargs: Mapping[str, ArgValue] = field(default_factory=dict)
    file: Optional[File] = None
    context: Optional[str] = None
    process_output: Any = "Mock output"
    configure_invoked: bool = False
    process_invoked: bool = False
    require_context: Optional[bool] = None

    def configure(self, *args, **kwargs):
        self.configure_invoked = True
        self.args = args
        self.kwargs = kwargs

    def process(self, file: File, context: Optional[str]) -> Any:
        self.process_invoked = True
        self.file = file
        self.context = context
        return self.process_output


@dataclass
class GeneratorTag(Tag):
    output_generator: Callable[[File, Optional[str]], Any]

    def process(self, file: File, context: Optional[str]) -> Any:
        return self.output_generator(file, context)
