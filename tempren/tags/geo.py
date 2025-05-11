from tempren.primitives import Tag


class PlaceNameTag(Tag):
    """Convert"""

    require_context = False

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is None
        return _calculate_hash(hashlib.md5(), file.absolute_path, CHUNK_SIZE)
