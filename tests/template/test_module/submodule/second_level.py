from typing import Optional

from tempren.primitives import File, Tag


class SecondLevelTag(Tag):
    require_context = None

    def process(self, path: File, context: Optional[str]) -> str:
        raise NotImplementedError()
