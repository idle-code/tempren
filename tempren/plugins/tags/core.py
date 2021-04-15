from pathlib import Path
from typing import Optional

from tempren.template.tree_elements import Tag


class CountTag(Tag):
    require_context = False
    counter: int
    step: int
    width: int

    def configure(self, start: int = 0, step: int = 1, width: int = 0):  # type: ignore
        if start < 0:
            raise ValueError("start have to be greater or equal 0")
        self.counter = start
        if step == 0:
            raise ValueError("step cannot be equal 0")
        self.step = step
        if width < 0:
            raise ValueError("width have to be greater or equal 0")
        self.width = width

    def process(self, path: Path, context: Optional[str]) -> str:
        value = self.counter
        self.counter += self.step
        return str(value).zfill(self.width)


class ExtTag(Tag):
    require_context = False

    def configure(self):  # type: ignore
        pass

    def process(self, path: Path, context: Optional[str]) -> str:
        return path.suffix.lstrip(".")


class DirnameTag(Tag):
    require_context = False

    def configure(self):  # type: ignore
        pass

    def process(self, path: Path, context: Optional[str]) -> str:
        return str(path.parent)
