from abc import ABC, abstractmethod
from typing import Any

from tempren.alias import TagAlias
from tempren.primitives import File, Tag


class FirstLevelTag(Tag):
    require_context = None

    def process(self, path: File, context: str | None) -> str:
        raise NotImplementedError()


class AbstractTag(Tag, ABC):
    require_context = None

    @abstractmethod
    def implementation_detail(self):
        raise NotImplementedError()

    def process(self, file: File, context: str | None) -> Any:
        self.implementation_detail()


class FirstLevelTagAlias(TagAlias):
    """%FirstLevel()-Alias"""

    pass
