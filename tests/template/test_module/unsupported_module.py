from tempren.primitives import File, Tag


class UnsupportedTag(Tag):
    require_context = None

    def process(self, file: File, context: str | None) -> str:
        raise NotImplementedError()


# Throw NotImplementedError to indicate that some dependencies for this module are missing
raise NotImplementedError()
