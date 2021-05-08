from pathlib import Path
from typing import Optional

import pytest

from tempren.template.tree_builder import (
    ConfigurationError,
    ContextForbiddenError,
    ContextMissingError,
    TagRegistry,
    UnknownTagError,
)
from tempren.template.tree_elements import Pattern, RawText, Tag, TagInstance

from .mocks import MockTag
from .test_tree_builder import parse


class TestTagRegistry:
    def test_register_tag__use_provided_name(self):
        registry = TagRegistry()

        registry.register_tag(MockTag, "FooBar")

        foobar_tag = registry.find_tag_factory("FooBar")
        assert foobar_tag

    def test_register_tag__generate_name_based_on_class(self):
        registry = TagRegistry()

        registry.register_tag(MockTag)

        mock_tag = registry.find_tag_factory("Mock")
        assert mock_tag

    def test_register_tag__cannot_deduce_name_from_class(self):
        class FakeExtractor(Tag):
            def configure(self, *args, **kwargs):
                pass

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        registry = TagRegistry()

        with pytest.raises(ValueError):
            registry.register_tag(FakeExtractor)

    def test_register_tag__register_existing_tag(self):
        registry = TagRegistry()
        registry.register_tag(MockTag)

        with pytest.raises(ValueError) as exc:
            registry.register_tag(MockTag)

        assert exc.match("already registered")

    def test_register_tag_factory__empty_name(self):
        registry = TagRegistry()

        def tag_factory(*args, **kwargs):
            pass

        with pytest.raises(ValueError) as exc:
            registry.register_tag_factory(tag_factory, "")

        exc.match("Invalid tag name")

    def test_bind__missing_tag(self):
        pattern = parse("%Nonexistent()")
        registry = TagRegistry()

        with pytest.raises(UnknownTagError) as exc:
            registry.bind(pattern)

        exc.match("Nonexistent")

    def test_bind__tag_factory_is_invoked(self):
        pattern = parse("%Dummy()")
        registry = TagRegistry()
        invoked = False

        def tag_factory(*args, **kwargs):
            nonlocal invoked
            invoked = True
            return MockTag()

        registry.register_tag_factory(tag_factory, "Dummy")

        registry.bind(pattern)

        assert invoked

    def test_bind__tag_factory_receives_positional_arguments(self):
        pattern = parse("%Dummy(1, 'text', true)")
        registry = TagRegistry()
        positional_args = None

        def tag_factory(*args, **kwargs):
            nonlocal positional_args
            positional_args = args
            return MockTag()

        registry.register_tag_factory(tag_factory, "Dummy")

        registry.bind(pattern)

        assert positional_args == (1, "text", True)

    def test_bind__tag_factory_receives_keyword_arguments(self):
        pattern = parse("%Dummy(a=1, b='text', c=true)")
        registry = TagRegistry()
        keyword_args = None

        def tag_factory(*args, **kwargs):
            nonlocal keyword_args
            keyword_args = kwargs
            return MockTag()

        registry.register_tag_factory(tag_factory, "Dummy")

        registry.bind(pattern)

        assert keyword_args == {"a": 1, "b": "text", "c": True}

    def test_default_tag_factory__configures_created_tag(self):
        pattern = parse("%Mock(1, b='text')")
        registry = TagRegistry()
        registry.register_tag(MockTag, "Mock")

        bound_pattern = registry.bind(pattern)

        expected_tag = MockTag(args=(1,), kwargs={"b": "text"}, configure_invoked=True)
        assert bound_pattern == Pattern([TagInstance(tag=expected_tag)])

    def test_default_tag_factory__configure_throws_wrong_parameter_name(self):
        pattern = parse("%Foo(bar='text')")
        registry = TagRegistry()

        class FooTag(Tag):
            def configure(self, foo: str):
                pytest.fail("This shouldn't execute")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        registry.register_tag(FooTag)

        with pytest.raises(ConfigurationError):
            registry.bind(pattern)

    def test_default_tag_factory__configure_rethrows_error_with_cause(self):
        pattern = parse("%Foo()")
        registry = TagRegistry()

        class FooTag(Tag):
            def configure(self):
                raise ValueError("Some configurations is not valid")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        registry.register_tag(FooTag)

        with pytest.raises(ConfigurationError) as exc:
            registry.bind(pattern)

        assert isinstance(exc.value.__cause__, ValueError)

    def test_bind__context_pattern_is_rewritten(self):
        pattern = parse("%Outer(name='outer'){%Inner(name='inner')}")
        registry = TagRegistry()
        registry.register_tag(MockTag, "Outer")
        registry.register_tag(MockTag, "Inner")

        bound_pattern = registry.bind(pattern)

        inner_tag = MockTag(kwargs={"name": "inner"}, configure_invoked=True)
        outer_tag = MockTag(kwargs={"name": "outer"}, configure_invoked=True)
        context_pattern = Pattern([TagInstance(tag=inner_tag)])
        assert bound_pattern == Pattern(
            [TagInstance(tag=outer_tag, context=context_pattern)]
        )

    def test_bind__raw_text_is_rewritten(self):
        pattern = parse("Just text")
        registry = TagRegistry()

        bound_pattern = registry.bind(pattern)

        assert bound_pattern == Pattern([RawText("Just text")])

    def test_bind__tag_requires_context_but_none_given(self):
        pattern = parse("%ContextRequired()")
        registry = TagRegistry()

        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        registry.register_tag_factory(required_context_tag_factory, "ContextRequired")

        with pytest.raises(ContextMissingError):
            registry.bind(pattern)

    def test_bind__tag_doesnt_accept_context_but_one_is_given(self):
        pattern = parse("%ContextForbidden(){context}")
        registry = TagRegistry()

        def forbidden_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=False)

        registry.register_tag_factory(forbidden_context_tag_factory, "ContextForbidden")

        with pytest.raises(ContextForbiddenError):
            registry.bind(pattern)

    def test_bind__tag_requires_context_and_one_given(self):
        pattern = parse("%ContextRequired(){context}")
        registry = TagRegistry()

        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        registry.register_tag_factory(required_context_tag_factory, "ContextRequired")

        bound_pattern = registry.bind(pattern)

        assert bound_pattern == Pattern(
            [
                TagInstance(
                    tag=MockTag(require_context=True),
                    context=Pattern([RawText("context")]),
                )
            ]
        )

    def test_register_tags_in_module__finds_first_level_tags(self):
        registry = TagRegistry()
        from .test_module import first_level

        registry.register_tags_in_module(first_level)

        first_level_tag_factory = registry.find_tag_factory("FirstLevel")
        assert first_level_tag_factory

    def test_register_tags_in_package__finds_first_level_tags(self):
        registry = TagRegistry()
        import tests.template.test_module

        registry.register_tags_in_package(tests.template.test_module)

        first_level_tag_factory = registry.find_tag_factory("FirstLevel")
        assert first_level_tag_factory

    def test_register_tags_in_package__finds_second_level_tags(self):
        registry = TagRegistry()
        import tests.template.test_module

        registry.register_tags_in_package(tests.template.test_module)

        second_level_tag_factory = registry.find_tag_factory("SecondLevel")
        assert second_level_tag_factory

    # TODO: add tests for documentation rewriting from tag class to tag factory
