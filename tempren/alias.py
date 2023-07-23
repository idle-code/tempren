from typing import Any, Optional, Type

from tempren.factories import TagFactoryFromClass
from tempren.primitives import File, Tag, TagName
from tempren.template.ast import Pattern
from tempren.template.compiler import TemplateCompiler


class TagAlias:
    """Base class for build-in aliases"""

    pattern_text: str

    def __init_subclass__(cls) -> None:
        if not cls.__doc__:  # NOCOVER: compile-time check
            raise ValueError(
                "Pattern template text should be specified in the derived class documentation"
            )
        cls.pattern_text = cls.__doc__
        super().__init_subclass__()


class AliasTag(Tag):
    """Alias for `{alias_text}`

    Every occurrence of this tag will be substituted with `{alias_text}` pattern.
    """

    require_context = False
    pattern: Pattern

    def __init__(self, pattern: Pattern) -> None:
        self.pattern = pattern

    def process(self, file: File, context: Optional[str]) -> Any:
        return self.pattern.process(file)


class AliasTagFactory(TagFactoryFromClass):
    """Produces AliasTag instances from given template pattern"""

    _pattern_text: str
    _compiler: TemplateCompiler

    @property
    def short_description(self) -> str:
        return self._render_description(super().short_description)

    @property
    def long_description(self) -> Optional[str]:
        long_description = super().long_description
        assert long_description, "AliasTag description changed"
        long_description = self._render_description(long_description)
        return long_description

    def __init__(
        self, alias_name: TagName, pattern_text: str, compiler: TemplateCompiler
    ):
        self._pattern_text = pattern_text
        self._compiler = compiler
        super().__init__(AliasTag, alias_name)

    def __call__(self, *args, **kwargs) -> Tag:
        pattern = self._compiler.compile(self._pattern_text)
        alias_tag = AliasTag(pattern)
        alias_tag.configure(*args, **kwargs)  # type: ignore
        return alias_tag

    def _render_description(self, description: str) -> str:
        return description.format(alias_text=self._pattern_text)


class AliasTagFactoryFromClass(AliasTagFactory):
    """Produces alias tags from (built-in) TagAlias classes"""

    _tag_alias_suffix = "TagAlias"

    def __init__(self, tag_alias_class: Type[TagAlias], compiler: TemplateCompiler):
        class_name = tag_alias_class.__name__
        if class_name.endswith(self._tag_alias_suffix):
            alias_tag_name = TagName(class_name[: -len(self._tag_alias_suffix)])
        else:
            raise ValueError(
                f"Could not determine tag alias name from tag alias class: {class_name}"
            )
        super().__init__(alias_tag_name, tag_alias_class.pattern_text, compiler)
