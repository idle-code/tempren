from pathlib import Path
from types import ModuleType
from typing import Optional

import pytest

from tempren.primitives import QualifiedTagName, Tag
from tempren.template.ast import Pattern, RawText, TagInstance
from tempren.template.registry import (
    AmbiguousTagError,
    ConfigurationError,
    ContextForbiddenError,
    ContextMissingError,
    TagCategory,
    TagRegistry,
    UnknownCategoryError,
    UnknownTagError,
)

from .mocks import MockTag
from .test_parser import parse


class TestTagCategory:
    def test_register_tag__use_provided_name(self):
        category = TagCategory("TestCategory")

        category.register_tag_class(MockTag, "FooBar")

        foobar_tag = category.find_tag_factory("FooBar")
        assert foobar_tag

    def test_register_tag__generate_name_based_on_class(self):
        category = TagCategory("TestCategory")

        category.register_tag_class(MockTag)

        mock_tag = category.find_tag_factory("Mock")
        assert mock_tag

    def test_register_tag__cannot_deduce_name_from_class(self):
        class FakeExtractor(Tag):
            def configure(self, *args, **kwargs):
                pass

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        category = TagCategory("TestCategory")

        with pytest.raises(ValueError):
            category.register_tag_class(FakeExtractor)

    def test_register_tag__register_existing_tag(self):
        category = TagCategory("TestCategory")
        category.register_tag_class(MockTag)

        with pytest.raises(ValueError) as exc:
            category.register_tag_class(MockTag)

        assert exc.match("already registered")

    # TODO: add tests for documentation rewriting from tag class to tag factory


class TestTagRegistry:
    def test_get_tag_factory__missing_factory(self):
        registry = TagRegistry()

        with pytest.raises(UnknownTagError):
            registry.get_tag_factory(QualifiedTagName("Mock"))

    def test_get_tag_factory__unknown_category(self):
        registry = TagRegistry()

        with pytest.raises(UnknownCategoryError):
            registry.get_tag_factory(QualifiedTagName("Mock", "Category"))

    def test_get_tag_factory__single_tag_no_category(self):
        registry = TagRegistry()
        category = registry.register_category("Category")
        category.register_tag_class(MockTag)

        tag_factory = registry.get_tag_factory(QualifiedTagName("Mock"))

        assert tag_factory is not None

    def test_get_tag_factory__single_tag_invalid_category(self):
        registry = TagRegistry()
        category = registry.register_category("Category")
        category.register_tag_class(MockTag)

        with pytest.raises(UnknownCategoryError):
            registry.get_tag_factory(QualifiedTagName("Mock", "OtherCategory"))

    def test_get_tag_factory__multiple_tags_no_category(self):
        registry = TagRegistry()
        category_a = registry.register_category("CategoryA")
        category_b = registry.register_category("CategoryB")
        category_a.register_tag_class(MockTag)
        category_b.register_tag_class(MockTag)

        with pytest.raises(AmbiguousTagError):
            registry.get_tag_factory(QualifiedTagName("Mock"))

    def test_get_tag_factory__multiple_tags_explicit_category(self):
        registry = TagRegistry()
        category_a = registry.register_category("CategoryA")
        category_b = registry.register_category("CategoryB")
        category_a.register_tag_class(MockTag)
        category_b.register_tag_class(MockTag)

        tag_b_factory = registry.get_tag_factory(QualifiedTagName("Mock", "CategoryB"))

        assert tag_b_factory is not None

    def test_bind__missing_tag(self):
        pattern = parse("%Nonexistent()")
        registry = TagRegistry()

        with pytest.raises(UnknownTagError) as exc:
            registry.bind(pattern)

        exc.match("Nonexistent")

    def test_bind__ambiguous_tag_name(self):
        pattern = parse("%Mock()")
        registry = TagRegistry()
        category_a = registry.register_category("CategoryA")
        category_b = registry.register_category("CategoryB")
        category_a.register_tag_class(MockTag)
        category_b.register_tag_class(MockTag)

        with pytest.raises(AmbiguousTagError) as exc:
            registry.bind(pattern)

        exc.match("Mock")
        exc.match("CategoryA")
        exc.match("CategoryB")

    def test_bind__tag_factory_is_invoked(self):
        pattern = parse("%Dummy()")
        registry = TagRegistry()
        category = registry.register_category("Test")
        invoked = False

        def tag_factory(*args, **kwargs):
            nonlocal invoked
            invoked = True
            return MockTag()

        category.register_tag_factory(tag_factory, "Dummy")

        registry.bind(pattern)

        assert invoked

    def test_bind__fully_qualified_tag_factory_is_invoked(self):
        pattern = parse("%Test.Dummy()")
        registry = TagRegistry()
        category = registry.register_category("Test")
        invoked = False

        def tag_factory(*args, **kwargs):
            nonlocal invoked
            invoked = True
            return MockTag()

        category.register_tag_factory(tag_factory, "Dummy")

        registry.bind(pattern)

        assert invoked

    def test_bind__tag_factory_receives_positional_arguments(self):
        pattern = parse("%Dummy(1, 'text', true)")
        registry = TagRegistry()
        category = registry.register_category("Test")
        positional_args = None

        def tag_factory(*args, **kwargs):
            nonlocal positional_args
            positional_args = args
            return MockTag()

        category.register_tag_factory(tag_factory, "Dummy")

        registry.bind(pattern)

        assert positional_args == (1, "text", True)

    def test_bind__tag_factory_receives_keyword_arguments(self):
        pattern = parse("%Dummy(a=1, b='text', c=true)")
        registry = TagRegistry()
        category = registry.register_category("Test")
        keyword_args = None

        def tag_factory(*args, **kwargs):
            nonlocal keyword_args
            keyword_args = kwargs
            return MockTag()

        category.register_tag_factory(tag_factory, "Dummy")

        registry.bind(pattern)

        assert keyword_args == {"a": 1, "b": "text", "c": True}

    def test_default_tag_factory__configures_created_tag(self):
        pattern = parse("%Mock(1, b='text')")
        registry = TagRegistry()
        category = registry.register_category("Test")
        category.register_tag_class(MockTag, "Mock")

        bound_pattern = registry.bind(pattern)

        expected_tag = MockTag(args=(1,), kwargs={"b": "text"}, configure_invoked=True)
        assert bound_pattern == Pattern([TagInstance(tag=expected_tag)])

    def test_default_tag_factory__configure_throws_wrong_parameter_name(self):
        pattern = parse("%Foo(bar='text')")
        registry = TagRegistry()
        category = registry.register_category("Test")

        class FooTag(Tag):
            def configure(self, foo: str):
                pytest.fail("This shouldn't execute")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        category.register_tag_class(FooTag)

        with pytest.raises(ConfigurationError):
            registry.bind(pattern)

    def test_default_tag_factory__configure_rethrows_error_with_cause(self):
        pattern = parse("%Foo()")
        registry = TagRegistry()
        category = registry.register_category("Test")

        class FooTag(Tag):
            def configure(self):
                raise ValueError("Some configurations is not valid")

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        category.register_tag_class(FooTag)

        with pytest.raises(ConfigurationError) as exc:
            registry.bind(pattern)

        assert isinstance(exc.value.__cause__, ValueError)

    def test_bind__context_pattern_is_rewritten(self):
        pattern = parse("%Outer(name='outer'){%Inner(name='inner')}")
        registry = TagRegistry()
        category = registry.register_category("Test")
        category.register_tag_class(MockTag, "Outer")
        category.register_tag_class(MockTag, "Inner")

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
        category = registry.register_category("Test")

        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        category.register_tag_factory(required_context_tag_factory, "ContextRequired")

        with pytest.raises(ContextMissingError):
            registry.bind(pattern)

    def test_bind__tag_doesnt_accept_context_but_one_is_given(self):
        pattern = parse("%ContextForbidden(){context}")
        registry = TagRegistry()
        category = registry.register_category("Test")

        def forbidden_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=False)

        category.register_tag_factory(forbidden_context_tag_factory, "ContextForbidden")

        with pytest.raises(ContextForbiddenError):
            registry.bind(pattern)

    def test_bind__tag_requires_context_and_one_given(self):
        pattern = parse("%ContextRequired(){context}")
        registry = TagRegistry()
        category = registry.register_category("Test")

        def required_context_tag_factory(*args, **kwargs):
            return MockTag(require_context=True)

        category.register_tag_factory(required_context_tag_factory, "ContextRequired")

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

        first_level_tag_factory = registry.get_tag_factory(
            QualifiedTagName("FirstLevel")
        )
        assert first_level_tag_factory

    def test_register_tags_in_module__excludes_abstract_tags(self):
        registry = TagRegistry()
        from .test_module import first_level

        registry.register_tags_in_module(first_level)

        with pytest.raises(UnknownTagError):
            registry.get_tag_factory(QualifiedTagName("Abstract"))

    @staticmethod
    def _load_module_from_path(module_path: Path) -> ModuleType:
        module_name = module_path.stem
        import importlib.util

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_register_tags_in_packageless_module__uses_module_name_as_category(
        self, tags_data_dir: Path
    ):
        registry = TagRegistry()
        packageless_tags_module = TestTagRegistry._load_module_from_path(
            tags_data_dir / "packageless_tags.py"
        )

        registry.register_tags_in_module(packageless_tags_module)

        packageless_tags_category = registry.find_category("packageless_tags")
        assert packageless_tags_category is not None

        assert registry.get_tag_factory(QualifiedTagName("Test", "packageless_tags"))

    def test_register_tags_in_package__finds_first_level_tags(self):
        registry = TagRegistry()
        import tests.template.test_module

        registry.register_tags_in_package(tests.template.test_module)

        first_level_tag_factory = registry.get_tag_factory(
            QualifiedTagName("FirstLevel")
        )
        assert first_level_tag_factory

    def test_register_tags_in_package__skips_unsupported_modules(self):
        registry = TagRegistry()
        import tests.template.test_module

        registry.register_tags_in_package(tests.template.test_module)

        with pytest.raises(UnknownTagError):
            registry.get_tag_factory(QualifiedTagName("Unsupported"))

    def test_register_tags_in_package__finds_second_level_tags(self):
        registry = TagRegistry()
        import tests.template.test_module

        registry.register_tags_in_package(tests.template.test_module)

        second_level_tag_factory = registry.get_tag_factory(
            QualifiedTagName("SecondLevel")
        )
        assert second_level_tag_factory

    def test_register_package__creates_categories(self):
        registry = TagRegistry()
        import tests.template.test_module

        registry.register_tags_in_package(tests.template.test_module)

        assert ["first_level", "second_level"] == registry.categories

    def test_register_already_existing_category__raises(self):
        registry = TagRegistry()
        registry.register_category("Existing")

        with pytest.raises(ValueError):
            registry.register_category("Existing")

    # TODO: Move binding and discovery tests from TestTagCategory
