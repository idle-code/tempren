import collections
from typing import Optional, Type

from tempren.template.tree_elements import Tag


class TagFactory:
    tag_name: str
    tag_class: Type

    def __init__(self, tag_class: Type, tag_name: Optional[str] = None):
        self.tag_class = tag_class
        if not tag_name:
            tag_class_name = tag_class.__name__
            if tag_class_name.endswith("Tag"):
                tag_name = tag_class_name[: -len("Tag")]
            else:
                raise ValueError(
                    f"Could not determine tag name from tag class: {tag_class_name}"
                )
        self.tag_name = tag_name

    def create_instance(self, context_present: bool, *args, **kwargs) -> Tag:
        return self.tag_class(*args, **kwargs, context_present=context_present)
