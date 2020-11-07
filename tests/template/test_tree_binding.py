from pathlib import Path
from typing import Optional

import pytest
from tempren.template.tree_builder import (
    ConfigurationError,
    ContextForbiddenError,
    ContextMissingError,
    TagTreeBinder,
    UnknownTagError,
)
from tempren.template.tree_elements import Pattern, RawText, Tag, TagInstance

from .mocks import MockTag
from .test_tree_builder import parse


class TestTagTreeBinder:
    def test_register_tag__use_provided_name(self):
        binder = TagTreeBinder()

        binder.register_tag(MockTag, "FooBar")

        foobar_tag = binder.find_tag_factory("FooBar")
        assert foobar_tag

    def test_register_tag__generate_name_based_on_class(self):
        binder = TagTreeBinder()

        binder.register_tag(MockTag)

        mock_tag = binder.find_tag_factory("Mock")
        assert mock_tag

    def test_register_tag__cannot_deduce_name_from_class(self):
        class FakeExtractor(Tag):
            def configure(self, *args, **kwargs):
                pass

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        binder = TagTreeBinder()

        with pytest.raises(ValueError):
            binder.register_tag(FakeExtractor)

    def test_register_tag__register_existing_tag(self):
        binder = TagTreeBinder()
        binder.register_tag(MockTag)

        with pytest.raises(ValueError) as exc:
            binder.register_tag(MockTag)

        assert exc.match("already registered")

    def test_bind__missing_tag(self):
        pattern = parse("%Nonexistent()")
        binder = TagTreeBinder()

        with pytest.raises(UnknownTagError) as exc:
            binder.bind(pattern)

        exc.match("Nonexistent")

    def test_bind__tag_factory_is_invoked(self):
        pattern = parse("%Dummy()")
        binder = TagTreeBinder()
        invoked = False

        def tag_factory(*args, **kwargs):
            nonlocal invoked
            invoked = True
            return MockTag()

        binder.register_tag_factory(tag_factory, "Dummy")

        binder.bind(pattern)

        assert invoked

    def test_bind__tag_factory_receives_positional_arguments(self):
        pattern = parse("%Dummy(1, 'text', true)")
        binder = TagTreeBinder()
        positional_args = None

        def tag_factory(*args, **kwargs):
            nonlocal positional_args
            positional_args = args
            return MockTag()

        binder.register_tag_factory(tag_factory, "Dummy")

        binder.bind(pattern)

        assert positional_args == (1, "text", True)

    def test_bind__tag_factory_receives_keyword_arguments(self):
        pattern = parse("%Dummy(a=1, b='text', c=true)")
        binder = TagTreeBinder()
        keyword_args = None

        def tag_factory(*args, **kwargs):
            nonlocal keyword_args
            keyword_args = kwargs
            return MockTag()

        binder.register_tag_factory(tag_factory, "Dummy")

        binder.bind(pattern)

        assert keyword_args == {"a": 1, "b": "text", "c": True}

    def test_default_tag_factory__configures_created_tag(self):
        pattern = parse("%Mock(1, b='text')")
        binder = TagTreeBinder()
        binder.register_tag(MockTag, "Mock")

        bound_pattern = binder.bind(pattern)

        expected_tag = MockTag(args=(1,), kwargs={"b": "text"}, configure_invoked=True)
        assert bound_pattern == Pattern([TagInstance(tag=expected_tag)])

    def test_default_tag_factory__configure_throws_wrong_parameter_name(self):
        pattern = parse("%Foo(bar='text')")
        binder = TagTreeBinder()

        class FooTag(Tag):
            def configure(self, foo: str):
                pytest.fail("This shouldn't execute")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        binder.register_tag(FooTag)

        with pytest.raises(ConfigurationError):
            binder.bind(pattern)

    def test_default_tag_factory__configure_rethrows_error_with_cause(self):
        pattern = parse("%Foo()")
        binder = TagTreeBinder()

        class FooTag(Tag):
            def configure(self):
                raise ValueError("Some configurations is not valid")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        binder.register_tag(FooTag)

        with pytest.raises(ConfigurationError) as exc:
            binder.bind(pattern)

        assert isinstance(exc.value.__cause__, ValueError)

    def test_bind__context_pattern_is_rewritten(self):
        pattern = parse("%Outer(name='outer'){%Inner(name='inner')}")
        binder = TagTreeBinder()
        binder.register_tag(MockTag, "Outer")
        binder.register_tag(MockTag, "Inner")

        bound_pattern = binder.bind(pattern)

        inner_tag = MockTag(kwargs={"name": "inner"}, configure_invoked=True)
        outer_tag = MockTag(kwargs={"name": "outer"}, configure_invoked=True)
        context_pattern = Pattern([TagInstance(tag=inner_tag)])
        assert bound_pattern == Pattern(
            [TagInstance(tag=outer_tag, context=context_pattern)]
        )

    def test_bind__raw_text_is_rewritten(self):
        pattern = parse("Just text")
        binder = TagTreeBinder()

        bound_pattern = binder.bind(pattern)

        assert bound_pattern == Pattern([RawText("Just text")])

    def test_bind__tag_requires_context_but_none_given(self):
        pattern = parse("%ContextRequired()")
        binder = TagTreeBinder()

        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        binder.register_tag_factory(required_context_tag_factory, "ContextRequired")

        with pytest.raises(ContextMissingError):
            binder.bind(pattern)

    def test_bind__tag_doesnt_accept_context_but_one_is_given(self):
        pattern = parse("%ContextForbidden(){context}")
        binder = TagTreeBinder()

        def forbidden_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=False)

        binder.register_tag_factory(forbidden_context_tag_factory, "ContextForbidden")

        with pytest.raises(ContextForbiddenError):
            binder.bind(pattern)

    def test_bind__tag_requires_context_and_one_given(self):
        pattern = parse("%ContextRequired(){context}")
        binder = TagTreeBinder()

        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        binder.register_tag_factory(required_context_tag_factory, "ContextRequired")

        bound_pattern = binder.bind(pattern)

        assert bound_pattern == Pattern(
            [
                TagInstance(
                    tag=MockTag(require_context=True),
                    context=Pattern([RawText("context")]),
                )
            ]
        )
