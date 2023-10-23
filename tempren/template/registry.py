import logging
from logging import Logger
from pathlib import Path
from typing import Dict, List, Optional, Type

from tempren.adhoc import AdHocTagFactoryFromExecutable
from tempren.factories import TagFactoryFromClass
from tempren.primitives import (
    CategoryName,
    Location,
    QualifiedTagName,
    Tag,
    TagFactory,
    TagName,
)
from tempren.template.exceptions import TagError, TemplateError


class TagCategory:
    log: Logger

    name: CategoryName
    description: Optional[str] = None
    tag_map: Dict[str, TagFactory]

    # CHECK: Move following to the TagRegistry? This would remove `tag_name` argument from `register_tag_class`
    _tag_class_suffix = "Tag"

    def __init__(self, name: CategoryName, description: Optional[str] = None):
        self.log = logging.getLogger(self.__class__.__name__)
        self.tag_map = {}
        self.name = name
        self.description = description

    def register_tag_class(
        self, tag_class: Type[Tag], tag_name: Optional[TagName] = None
    ):
        if not tag_name:
            tag_class_name = tag_class.__name__
            if tag_class_name.endswith(self._tag_class_suffix):
                tag_name = TagName(tag_class_name[: -len(self._tag_class_suffix)])
            else:
                raise ValueError(
                    f"Could not determine tag name from tag class: {tag_class_name}"
                )

        class_tag_factory = TagFactoryFromClass(tag_class, tag_name)
        self.log.debug(
            f"Registering class {tag_class} as {class_tag_factory.tag_name} tag"
        )
        self.register_tag_factory(class_tag_factory, tag_name)

    def register_tag_from_executable(self, exec_path: Path, tag_name: TagName):
        executable_tag_factory = AdHocTagFactoryFromExecutable(exec_path, tag_name)
        self.log.debug(
            f"Registering executable {exec_path} as {executable_tag_factory.tag_name} tag"
        )
        self.register_tag_factory(executable_tag_factory, tag_name)

    def register_tag_factory(
        self, tag_factory: TagFactory, tag_name: Optional[TagName] = None
    ):
        if tag_name is None:
            tag_name = tag_factory.tag_name
        if not tag_name:
            raise ValueError(f"Invalid tag name '{repr(tag_name)}'")
        if tag_name in self.tag_map:
            raise ValueError(f"Factory for tag '{tag_name}' already registered")
        self.tag_map[tag_name] = tag_factory

    def find_tag_factory(self, tag_name: TagName) -> Optional[TagFactory]:
        return self.tag_map.get(tag_name, None)


class TagRegistry:
    log: Logger
    category_map: Dict[CategoryName, TagCategory]

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.category_map = {}

    @property
    def categories(self) -> List[CategoryName]:
        return sorted(self.category_map.keys())

    def find_category(self, category_name: CategoryName) -> Optional[TagCategory]:
        category = self.category_map.get(category_name, None)
        if category:
            return category
        category_name = CategoryName(category_name.lower())
        return self.category_map.get(category_name, None)

    def get_tag_factory(self, tag_name: QualifiedTagName) -> TagFactory:
        if tag_name.category is None:
            return self._get_tag_factory_by_unique_name(tag_name.name)
        else:
            return self._get_tag_factory_by_qualified_name(tag_name)

    def _get_tag_factory_by_unique_name(self, tag_name: TagName) -> TagFactory:
        # In case there are tags with the same name in multiple categories,
        # category name have to be specified explicitly
        found_tag_factories: Dict[CategoryName, TagFactory] = {}
        for category in self.category_map.values():
            tag_factory = category.find_tag_factory(tag_name)
            if tag_factory:
                found_tag_factories[category.name] = tag_factory

        if not found_tag_factories:
            raise UnknownNameError(QualifiedTagName(tag_name))
        elif len(found_tag_factories) > 1:
            category_names = sorted(list(found_tag_factories.keys()))
            raise AmbiguousNameError(QualifiedTagName(tag_name), category_names)

        return next(iter(found_tag_factories.values()))

    def _get_tag_factory_by_qualified_name(
        self, qualified_name: QualifiedTagName
    ) -> TagFactory:
        assert qualified_name.category
        tag_category = self.find_category(qualified_name.category)
        if tag_category is None:
            raise UnknownCategoryError(qualified_name)

        tag_factory = tag_category.find_tag_factory(qualified_name.name)
        if tag_factory is None:
            raise UnknownNameError(qualified_name)

        return tag_factory

    def register_category(
        self, category_name: CategoryName, description: Optional[str] = None
    ) -> TagCategory:
        # TODO: This method should receive already build (non-empty) TagCategory
        if self.find_category(category_name) is not None:
            raise ValueError(f"Category '{category_name}' already registered")
        new_category = TagCategory(category_name)
        self.category_map[category_name] = new_category
        return new_category


class UnknownNameError(TagError):
    def __init__(self, tag_name: QualifiedTagName):
        super().__init__(tag_name, f"Unknown tag name: {tag_name.name}")

    def with_location(self, whole_name_location: Location) -> "TemplateError":
        if not self.tag_name.category:
            return super().with_location(whole_name_location)
        name_location = Location(
            whole_name_location.line,
            whole_name_location.column + len(self.tag_name.category) + 1,
            len(self.tag_name.name),
        )
        return super().with_location(name_location)


class UnknownCategoryError(TagError):
    def __init__(self, tag_name: QualifiedTagName):
        super().__init__(tag_name, f"Unknown category name: {tag_name.category}")

    def with_location(self, whole_name_location: Location) -> "TemplateError":
        assert self.tag_name.category
        category_location = Location(
            whole_name_location.line,
            whole_name_location.column,
            len(self.tag_name.category),
        )
        return super().with_location(category_location)


class AmbiguousNameError(TagError):
    category_names: List[CategoryName]

    def __init__(self, tag_name: QualifiedTagName, category_names: List[CategoryName]):
        super().__init__(
            tag_name,
            f"This tag name is present in multiple categories: {', '.join(category_names)}",
        )
        self.category_names = category_names
