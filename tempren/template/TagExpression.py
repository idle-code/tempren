from dataclasses import dataclass, field
from typing import List

from .TagExpressionElement import TagExpressionElement


@dataclass
class TagExpression(TagExpressionElement):
    sub_elements: List[TagExpressionElement] = field(default_factory=list)

    def __str__(self) -> str:
        return "".join(map(str, self.sub_elements))
