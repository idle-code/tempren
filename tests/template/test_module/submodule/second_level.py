from tempren.alias import TagAlias
from tempren.primitives import File, Tag


class SecondLevelTag(Tag):
    require_context = None

    def process(self, path: File, context: str | None) -> str:
        raise NotImplementedError()
