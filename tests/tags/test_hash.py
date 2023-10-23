from pathlib import Path

from tempren.primitives import File
from tempren.tags.hash import Crc32Tag, Md5Tag, Sha1Tag, Sha224Tag, Sha256Tag


class TestMd5Tag:
    def test_text_file_hash(self, text_data_dir: Path):
        tag = Md5Tag()
        hello_file = File(text_data_dir, Path("hello.txt"))

        result = tag.process(hello_file, None)

        assert result == "09f7e02f1290be211da707a266f153b3"


class TestSha1Tag:
    def test_text_file_hash(self, text_data_dir: Path):
        tag = Sha1Tag()
        hello_file = File(text_data_dir, Path("hello.txt"))

        result = tag.process(hello_file, None)

        assert result == "1d229271928d3f9e2bb0375bd6ce5db6c6d348d9"


class TestSha256Tag:
    def test_text_file_hash(self, text_data_dir: Path):
        tag = Sha256Tag()
        hello_file = File(text_data_dir, Path("hello.txt"))

        result = tag.process(hello_file, None)

        assert (
            result == "66a045b452102c59d840ec097d59d9467e13a3f34f6494e539ffd32c1bb35f18"
        )


class TestSha224Tag:
    def test_text_file_hash(self, text_data_dir: Path):
        tag = Sha224Tag()
        hello_file = File(text_data_dir, Path("hello.txt"))

        result = tag.process(hello_file, None)

        assert result == "acbe28e133c6e7e8cc740d5c70875c995e0b5950aa010b25649eb540"


class TestCrc32Tag:
    def test_text_file_hash(self, text_data_dir: Path):
        tag = Crc32Tag()
        hello_file = File(text_data_dir, Path("hello.txt"))

        result = tag.process(hello_file, None)

        assert result == "31963516"
