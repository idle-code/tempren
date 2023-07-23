import pytest

from tempren.alias import AliasTag, TagAlias, TagFactoryFromAlias
from tempren.primitives import File
from tempren.template.ast import Pattern, RawText
from tempren.template.compiler import TemplateCompiler


class DummyCompiler:
    def compile(self, template_text: str) -> Pattern:
        return Pattern([RawText(template_text)])


@pytest.fixture
def compiler() -> TemplateCompiler:
    return DummyCompiler()


class FooBarTagAlias(TagAlias):
    """Foo bar"""


class TestTagFactoryFromAlias:
    def test_short_description(self, compiler: TemplateCompiler):
        factory = TagFactoryFromAlias(FooBarTagAlias, compiler)
        assert "Alias" in factory.short_description
        assert "Foo bar" in factory.short_description

    def test_long_description(self, compiler: TemplateCompiler):
        factory = TagFactoryFromAlias(FooBarTagAlias, compiler)
        assert "Foo bar" in factory.long_description

    def test_tag_alias_without_suffix(self, compiler: TemplateCompiler):
        class _InvalidAlias(TagAlias):
            """Spam"""

        with pytest.raises(ValueError) as exc:
            TagFactoryFromAlias(_InvalidAlias, compiler)

        assert exc.match("tag alias name")

    def test_specify_args_for_alias(self, compiler):
        factory = TagFactoryFromAlias(FooBarTagAlias, compiler)

        with pytest.raises(TypeError) as exc:
            factory(1, 2)

        assert exc.match("positional argument")

    def test_specify_keyword_args_for_alias(self, compiler):
        factory = TagFactoryFromAlias(FooBarTagAlias, compiler)

        with pytest.raises(TypeError) as exc:
            factory(foo="bar")

        assert exc.match("unexpected keyword argument")


class TestAliasTag:
    def test_redirects_processing_to_passed_pattern(self, nonexistent_file: File):
        pattern = Pattern([RawText("Spam")])
        alias_tag = AliasTag(pattern)

        result = alias_tag.process(nonexistent_file, None)

        assert result == "Spam"
