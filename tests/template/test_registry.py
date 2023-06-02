from pathlib import Path
from types import ModuleType
from typing import Optional

import pytest

from tempren.primitives import CategoryName, QualifiedTagName, Tag, TagName
from tempren.template.registry import (
    AliasRegistry,
    AmbiguousNameError,
    TagCategory,
    TagRegistry,
    UnknownCategoryError,
    UnknownNameError,
)

from .mocks import MockTag


class TestTagCategory:
    def test_register_tag__use_provided_name(self):
        category = TagCategory(CategoryName("TestCategory"))

        category.register_tag_class(MockTag, TagName("FooBar"))

        foobar_tag = category.find_tag_factory(TagName("FooBar"))
        assert foobar_tag

    def test_register_tag__generate_name_based_on_class(self):
        category = TagCategory(CategoryName("TestCategory"))

        category.register_tag_class(MockTag)

        mock_tag = category.find_tag_factory(TagName("Mock"))
        assert mock_tag

    def test_register_tag__cannot_deduce_name_from_class(self):
        class FakeExtractor(Tag):
            def configure(self, *args, **kwargs):
                pass

            def process(self, path: Path, context: Optional[str]) -> str:
                pass

        category = TagCategory(CategoryName("TestCategory"))

        with pytest.raises(ValueError):
            category.register_tag_class(FakeExtractor)

    def test_register_tag__register_existing_tag(self):
        category = TagCategory(CategoryName("TestCategory"))
        category.register_tag_class(MockTag)

        with pytest.raises(ValueError) as exc:
            category.register_tag_class(MockTag)

        assert exc.match("already registered")

    # TODO: add tests for documentation rewriting from tag class to tag factory


def qualified_name(name: str, category: Optional[str] = None) -> QualifiedTagName:
    if category:
        return QualifiedTagName(TagName(name), CategoryName(category))
    return QualifiedTagName(TagName(name))


class TestTagRegistry:
    def test_get_tag_factory__missing_factory(self):
        registry = TagRegistry()

        with pytest.raises(UnknownNameError):
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

        with pytest.raises(AmbiguousNameError):
            registry.get_tag_factory(QualifiedTagName("Mock"))

    def test_get_tag_factory__multiple_tags_explicit_category(self):
        registry = TagRegistry()
        category_a = registry.register_category("CategoryA")
        category_b = registry.register_category("CategoryB")
        category_a.register_tag_class(MockTag)
        category_b.register_tag_class(MockTag)

        tag_b_factory = registry.get_tag_factory(QualifiedTagName("Mock", "CategoryB"))

        assert tag_b_factory is not None

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

        with pytest.raises(UnknownNameError):
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

        with pytest.raises(UnknownNameError):
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

    def test_register_existing_category__raises(self):
        registry = TagRegistry()
        existing_category_name = CategoryName("Existing")
        registry.register_category(existing_category_name)

        with pytest.raises(ValueError):
            registry.register_category(existing_category_name)

    # TODO: Move binding and discovery tests from TestTagCategory


class TestAliasRegistry:
    def test_find_nonexistent_category_alias(self):
        registry = AliasRegistry()
        registry.register_alias(
            qualified_name("Alias", "TestCategory"), "Alias pattern"
        )

        alias = registry.find_alias(qualified_name("Tag", "TestCategory"))

        assert alias is None

    def test_find_nonexistent_alias(self):
        registry = AliasRegistry()

        alias = registry.find_alias(qualified_name("TestCategory", "Tag"))

        assert alias is None

    def test_find_registered_alias_with_category(self):
        registry = AliasRegistry()
        alias_name = qualified_name("Alias", "TestCategory")
        registry.register_alias(alias_name, "Alias pattern")

        alias = registry.find_alias(alias_name)

        assert alias is not None
        assert alias.pattern_text == "Alias pattern"

    def test_find_registered_alias_without_category(self):
        registry = AliasRegistry()
        alias_name = qualified_name("Alias", "TestCategory")
        registry.register_alias(alias_name, "Alias pattern")

        alias = registry.find_alias(qualified_name("Alias"))

        assert alias is not None
        assert alias.pattern_text == "Alias pattern"

    def test_find_common_name(self):
        registry = AliasRegistry()
        alias_name = qualified_name("Alias", "TestCategory")
        other_alias_name = qualified_name("Alias", "OtherCategory")
        registry.register_alias(alias_name, "Alias pattern")
        registry.register_alias(other_alias_name, "Other alias pattern")

        with pytest.raises(AmbiguousNameError) as exc:
            registry.find_alias(qualified_name("Alias"))

        assert "TestCategory" in exc.value.category_names
        assert "OtherCategory" in exc.value.category_names

    def test_register_alias_over_existing_alias(self):
        registry = AliasRegistry()
        alias_name = qualified_name("Alias", "TestCategory")
        registry.register_alias(alias_name, "Alias pattern")

        with pytest.raises(ValueError) as exc:
            registry.register_alias(alias_name, "Alias pattern")

        assert exc.match("already registered")

    def test_find_alias_registered_without_category(self):
        registry = AliasRegistry()
        alias_name = qualified_name("Alias")

        registry.register_alias(alias_name, "Alias pattern")

        alias = registry.find_alias(alias_name)
        assert alias is not None

    def test_register_alias_without_category(self):
        registry = AliasRegistry()
        alias_name = qualified_name("Alias")

        registry.register_alias(alias_name, "Alias pattern")

        default_category_alias = next(registry.aliases())
        assert default_category_alias[0].name == "Alias"
        assert default_category_alias[0].category == "Aliases"
