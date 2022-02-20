import hashlib
import zlib
from pathlib import Path
from typing import Optional

from tempren.template.tree_elements import Tag

CHUNK_SIZE = 4096


def _calculate_hash(algorithm, path: Path, chunk_size: int) -> str:
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            algorithm.update(chunk)
    return algorithm.hexdigest()


class Md5Tag(Tag):
    """Calculates MD5 hash of the file"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is None
        return _calculate_hash(hashlib.md5(), path, CHUNK_SIZE)


class Sha1Tag(Tag):
    """Calculates SHA1 hash of the file"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is None
        return _calculate_hash(hashlib.sha1(), path, CHUNK_SIZE)


class Sha256Tag(Tag):
    """Calculates SHA256 hash of the file"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is None
        return _calculate_hash(hashlib.sha256(), path, CHUNK_SIZE)


class Sha224Tag(Tag):
    """Calculates SHA224 hash of the file"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is None
        return _calculate_hash(hashlib.sha224(), path, CHUNK_SIZE)


class Crc32Tag(Tag):
    """Calculates CRC32 hash of the file"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> str:
        assert context is None
        hash_value = 0
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                hash_value = zlib.crc32(chunk, hash_value)
        return f"{hash_value:08x}"
