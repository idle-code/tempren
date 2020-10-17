from dataclasses import dataclass

from .TagExpressionElement import TagExpressionElement


@dataclass
class RawText(TagExpressionElement):
    text: str

    def __str__(self) -> str:
        return self.text
