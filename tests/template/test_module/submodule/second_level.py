from typing import Optional

from tempren.primitives import File, Tag, TagAlias


class SecondLevelTag(Tag):
    require_context = None

    def process(self, path: File, context: Optional[str]) -> str:
        raise NotImplementedError()
