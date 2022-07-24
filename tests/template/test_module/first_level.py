from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from tempren.path_generator import File
from tempren.template.tree_elements import Tag


class FirstLevelTag(Tag):
    require_context = None

    def process(self, path: Path, context: Optional[str]) -> str:
        raise NotImplementedError()


class AbstractTag(Tag, ABC):
    require_context = None

    @abstractmethod
    def implementation_detail(self):
        raise NotImplementedError()

    def process(self, file: File, context: Optional[str]) -> Any:
        self.implementation_detail()
