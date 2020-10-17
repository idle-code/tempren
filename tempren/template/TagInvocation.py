from dataclasses import dataclass

from .TagExpressionElement import TagExpressionElement


@dataclass
class TagInvocation(TagExpressionElement):
    tag_name: str

    def __str__(self):
        raise NotImplementedError()
