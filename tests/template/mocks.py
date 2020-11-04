from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Tuple

from tempren.template.tree_builder import ArgValue
from tempren.template.tree_elements import Tag


@dataclass
class MockTag(Tag):
    args: Tuple[ArgValue, ...] = ()
    kwargs: Mapping[str, ArgValue] = field(default_factory=dict)
    path: Optional[Path] = None
    context: Optional[str] = None
    process_output: str = "Mock output"
    configure_invoked: bool = False
    process_invoked: bool = False

    def configure(self, *args, **kwargs):
        self.configure_invoked = True
        self.args = args
        self.kwargs = kwargs

    def process(self, path: Path, context: Optional[str]) -> str:
        self.process_invoked = True
        self.path = path
        self.context = context
        return self.process_output
