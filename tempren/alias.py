from dataclasses import dataclass
from typing import Any, Optional, Type

from tempren.factories import TagFactoryFromClass
from tempren.primitives import File, Tag, TagName
from tempren.template.ast import Pattern
from tempren.template.compiler import TemplateCompiler


@dataclass
class Alias:
    """Pattern alias interface"""

    pattern_text: str


class TagAlias(Alias):
    """Base class for build-in aliases"""

    def __init_subclass__(cls) -> None:
        if not cls.__doc__:  # NOCOVER: compile-time check
            raise ValueError(
                "Pattern template text should be specified in the derived class documentation"
            )
        cls.pattern_text = cls.__doc__
        super().__init_subclass__()


class TagFactoryFromAlias(TagFactoryFromClass):
    _tag_alias_suffix = "TagAlias"
    _alias_text: str
    _compiled_pattern: Pattern
    _compiler: TemplateCompiler

    @property
    def short_description(self) -> str:
        return self._render_description(super().short_description)

    @property
    def long_description(self) -> Optional[str]:
        long_description = super().long_description
        long_description = self._render_description(long_description)
        return long_description

    def __init__(self, tag_alias_class: Type[TagAlias], compiler: TemplateCompiler):
        self._alias_text = tag_alias_class.pattern_text
        self._compiler = compiler
        class_name = tag_alias_class.__name__
        if class_name.endswith(self._tag_alias_suffix):
            tag_name = TagName(class_name[: -len(self._tag_alias_suffix)])
        else:
            raise ValueError(
                f"Could not determine tag alias name from tag alias class: {class_name}"
            )
        super().__init__(AliasTag, tag_name)

    def __call__(self, *args, **kwargs) -> Tag:
        pattern = self._compiler.compile(self._alias_text)
        alias_tag = AliasTag(pattern)
        alias_tag.configure(*args, **kwargs)  # type: ignore
        return alias_tag

    def _render_description(self, description: str) -> str:
        return description.format(alias_text=self._alias_text)


class AliasTag(Tag):
    """Alias for `{alias_text}`

    Every occurrence of this tag will be substituted with `{alias_text}`.
    """

    require_context = False
    pattern: Pattern

    def __init__(self, pattern: Pattern) -> None:
        self.pattern = pattern

    def process(self, file: File, context: Optional[str]) -> Any:
        return self.pattern.process(file)
