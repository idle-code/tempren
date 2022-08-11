from typing import Optional

from tempren.path_generator import File
from tempren.template.tree_elements import Tag


class UnsupportedTag(Tag):
    require_context = None

    def process(self, file: File, context: Optional[str]) -> str:
        raise NotImplementedError()


# Throw NotImplementedError to indicate that some dependencies for this module are missing
raise NotImplementedError()
