from pathlib import Path
from typing import Callable, Dict, Optional, Type, Union

import pytest

from tempren.primitives import CategoryName, Tag, TagFactory, TagName
from tempren.template.ast import RawText, TagInstance
from tempren.template.compiler import (
    ConfigurationError,
    ContextForbiddenError,
    ContextMissingError,
    TemplateCompiler,
)
from tempren.template.registry import AmbiguousNameError, TagRegistry, UnknownNameError

from ..conftest import pattern_from
from .mocks import MockTag


class CallableTagFactory(TagFactory):
    @property
    def tag_name(self) -> TagName:
        return self._tag_name

    @property
    def configuration_signature(self) -> str:
        raise NotImplementedError()

    @property
    def short_description(self) -> str:
        raise NotImplementedError()

    @property
    def long_description(self) -> Optional[str]:
        raise NotImplementedError()

    def __call__(self, *args, **kwargs) -> Tag:
        return self._factory_function(*args, **kwargs)

    def __init__(self, factory_function: Callable, tag_name: TagName):
        self._factory_function = factory_function
        self._tag_name = tag_name


class TestTemplateCompiler:
    def create_compiler(
        self,
        registry_representation: Optional[
            Dict[str, Dict[str, Union[Type[Tag], Callable]]]
        ] = None,
    ) -> TemplateCompiler:
        registry = TagRegistry()
        if registry_representation:
            for category_name, tags in registry_representation.items():
                category = registry.register_category(CategoryName(category_name))
                for tag_name, factory in tags.items():
                    if isinstance(factory, type):
                        category.register_tag_class(factory, TagName(tag_name))
                    elif callable(factory):
                        category.register_tag_factory(
                            CallableTagFactory(factory, TagName(tag_name)),
                            TagName(tag_name),
                        )
                    else:
                        raise NotImplementedError()

        return TemplateCompiler(registry)

    def test_compile__missing_tag(self):
        compiler = self.create_compiler()

        with pytest.raises(UnknownNameError) as exc:
            compiler.compile("%Nonexistent()")

        exc.match("Nonexistent")

    def test_compile__ambiguous_tag_name(self):
        compiler = self.create_compiler(
            {"CategoryA": {"Mock": MockTag}, "CategoryB": {"Mock": MockTag}}
        )

        with pytest.raises(AmbiguousNameError) as exc:
            compiler.compile("%Mock()")

        exc.match("Mock")
        exc.match("CategoryA")
        exc.match("CategoryB")

    def test_compile__tag_factory_is_invoked(self):
        invoked = False

        def tag_factory(*args, **kwargs):
            nonlocal invoked
            invoked = True
            return MockTag()

        compiler = self.create_compiler({"Test": {"Dummy": tag_factory}})

        compiler.compile("%Dummy()")

        assert invoked

    def test_compile__fully_qualified_tag_factory_is_invoked(self):
        invoked = False

        def tag_factory(*args, **kwargs):
            nonlocal invoked
            invoked = True
            return MockTag()

        compiler = self.create_compiler({"Test": {"Dummy": tag_factory}})

        compiler.compile("%Test.Dummy()")

        assert invoked

    def test_compile__tag_factory_receives_positional_arguments(self):
        positional_args = None

        def tag_factory(*args, **kwargs):
            nonlocal positional_args
            positional_args = args
            return MockTag()

        compiler = self.create_compiler({"Test": {"Dummy": tag_factory}})

        compiler.compile("%Dummy(1, 'text', true)")

        assert positional_args == (1, "text", True)

    def test_compile__tag_factory_receives_keyword_arguments(self):
        keyword_args = None

        def tag_factory(*args, **kwargs):
            nonlocal keyword_args
            keyword_args = kwargs
            return MockTag()

        compiler = self.create_compiler({"Test": {"Dummy": tag_factory}})

        compiler.compile("%Dummy(a=1, b='text', c=true)")

        assert keyword_args == {"a": 1, "b": "text", "c": True}

    def test_default_tag_factory__configures_created_tag(self):
        compiler = self.create_compiler({"Test": {"Mock": MockTag}})

        bound_pattern = compiler.compile("%Mock(1, b='text')")

        expected_tag = MockTag(args=(1,), kwargs={"b": "text"}, configure_invoked=True)
        assert bound_pattern == pattern_from(TagInstance(tag=expected_tag))

    def test_default_tag_factory__configure_throws_wrong_parameter_name(self):
        class FooTag(Tag):
            def configure(self, foo: str):
                pytest.fail("This shouldn't execute")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        compiler = self.create_compiler({"Test": {"Foo": FooTag}})

        with pytest.raises(ConfigurationError):
            compiler.compile("%Foo(bar='text')")

    def test_default_tag_factory__configure_rethrows_error_with_cause(self):
        class FooTag(Tag):
            def configure(self):
                raise ValueError("Some configurations is not valid")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        compiler = self.create_compiler({"Test": {"Foo": FooTag}})

        with pytest.raises(ConfigurationError) as exc:
            compiler.compile("%Foo()")

        assert isinstance(exc.value.__cause__, ValueError)

    def test_compile__context_pattern_is_rewritten(self):
        compiler = self.create_compiler(
            {
                "Test": {
                    "Inner": MockTag,
                    "Outer": MockTag,
                }
            }
        )

        bound_pattern = compiler.compile("%Outer(name='outer'){%Inner(name='inner')}")

        inner_tag = MockTag(kwargs={"name": "inner"}, configure_invoked=True)
        outer_tag = MockTag(kwargs={"name": "outer"}, configure_invoked=True)
        context_pattern = pattern_from(TagInstance(tag=inner_tag))
        list1 = [TagInstance(tag=outer_tag, context=context_pattern)]
        assert bound_pattern == pattern_from(*list1)

    def test_compile__raw_text_is_rewritten(self):
        compiler = self.create_compiler()

        bound_pattern = compiler.compile("Just text")

        assert bound_pattern == pattern_from(RawText("Just text"))

    def test_compile__tag_requires_context_but_none_given(self):
        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        compiler = self.create_compiler(
            {"Test": {"ContextRequired": required_context_tag_factory}}
        )

        with pytest.raises(ContextMissingError):
            compiler.compile("%ContextRequired()")

    def test_compile__tag_doesnt_accept_context_but_one_is_given(self):
        def forbidden_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=False)

        compiler = self.create_compiler(
            {"Test": {"ContextForbidden": forbidden_context_tag_factory}}
        )

        with pytest.raises(ContextForbiddenError):
            compiler.compile("%ContextForbidden(){context}")

    def test_compile__tag_requires_context_and_one_given(self):
        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        compiler = self.create_compiler(
            {"Test": {"ContextRequired": required_context_tag_factory}}
        )

        bound_pattern = compiler.compile("%ContextRequired(){context}")

        assert bound_pattern == pattern_from(
            TagInstance(
                tag=MockTag(require_context=True),
                context=pattern_from(RawText("context")),
            )
        )
