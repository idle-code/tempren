from typing import Optional

from tempren.path_generator import File
from tempren.template.tree_elements import Tag


class SecondLevelTag(Tag):
    require_context = None

    def process(self, path: File, context: Optional[str]) -> str:
        raise NotImplementedError()
