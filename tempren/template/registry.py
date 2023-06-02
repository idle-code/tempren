import importlib
import inspect
import logging
import pkgutil
from itertools import starmap
from logging import Logger
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterator, List, Optional, Tuple, Type

from tempren.adhoc import TagFactoryFromExecutable
from tempren.factories import TagFactoryFromClass
from tempren.primitives import (
    Alias,
    CategoryName,
    Location,
    QualifiedTagName,
    Tag,
    TagFactory,
    TagName,
)
from tempren.template.ast import Pattern, PatternElement, TagInstance, TagPlaceholder
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
        executable_tag_factory = TagFactoryFromExecutable(exec_path, tag_name)
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
    _tag_class_suffix = "Tag"
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
            return self._get_tag_factory_by_unique_name(tag_name)
        else:
            return self._get_tag_factory_by_qualified_name(tag_name)

    def _get_tag_factory_by_unique_name(
        self, qualified_name: QualifiedTagName
    ) -> TagFactory:
        # In case there are tags with the same name in multiple categories,
        # category name have to be specified explicitly
        found_tag_factories: Dict[CategoryName, TagFactory] = {}
        for category in self.category_map.values():
            tag_factory = category.find_tag_factory(qualified_name.name)
            if tag_factory:
                found_tag_factories[category.name] = tag_factory

        if not found_tag_factories:
            raise UnknownNameError(qualified_name)
        elif len(found_tag_factories) > 1:
            category_names = sorted(list(found_tag_factories.keys()))
            raise AmbiguousNameError(qualified_name, category_names)

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

    def bind(
        self, pattern: Pattern
    ) -> Pattern:  # TODO: Move to the TemplateCompiler class
        return self._rewrite_pattern(pattern)

    def _rewrite_pattern(self, pattern: Pattern) -> Pattern:
        new_elements: List[PatternElement] = []
        for element in pattern.sub_elements:
            if isinstance(element, TagPlaceholder):
                new_elements.append(self._rewrite_tag_placeholder(element))
            else:
                new_elements.append(element)
        bound_pattern = Pattern(new_elements)
        bound_pattern.source_representation = pattern.source_representation
        return bound_pattern

    def _rewrite_tag_placeholder(self, tag_placeholder: TagPlaceholder) -> TagInstance:
        try:
            tag_factory = self.get_tag_factory(tag_placeholder.tag_name)

            self.log.debug(
                "Creating tag '%s' with arguments: %s %s",
                tag_placeholder.tag_name,
                tag_placeholder.args,
                tag_placeholder.kwargs,
            )
            tag = tag_factory(*tag_placeholder.args, **tag_placeholder.kwargs)
        except TemplateError as template_error:
            raise template_error.with_location(tag_placeholder.location)
        except Exception as exc:
            raise ConfigurationError(tag_placeholder.tag_name, str(exc)).with_location(
                tag_placeholder.location
            ) from exc

        if tag.require_context is not None:
            if tag_placeholder.context and not tag.require_context:
                raise ContextForbiddenError(tag_placeholder.tag_name).with_location(
                    tag_placeholder.location
                )
            elif tag_placeholder.context is None and tag.require_context:
                raise ContextMissingError(tag_placeholder.tag_name).with_location(
                    tag_placeholder.location
                )

        context_pattern: Optional[Pattern] = None
        if tag_placeholder.context:
            context_pattern = self._rewrite_pattern(tag_placeholder.context)

        return TagInstance(tag, context=context_pattern)

    def register_category(
        self, category_name: CategoryName, description: Optional[str] = None
    ) -> TagCategory:
        # TODO: This method should receive already build (non-empty) TagCategory
        if self.find_category(category_name) is not None:
            raise ValueError(f"Category '{category_name}' already registered")
        new_category = TagCategory(category_name)
        self.category_map[category_name] = new_category
        return new_category

    def register_tags_in_module(self, module: ModuleType):
        self.log.debug(f"Discovering tags in module '{module}'")

        if module.__package__:
            category_name = CategoryName(module.__name__[len(module.__package__) + 1 :])
        else:
            category_name = CategoryName(module.__name__)

        def is_tag_class(klass: type):
            if (
                not inspect.isclass(klass)
                or not issubclass(klass, Tag)
                or inspect.isabstract(klass)
                or klass == Tag
            ):
                return False
            return klass.__name__.endswith(self._tag_class_suffix)

        # TODO: do not register empty modules
        module_category = self.register_category(category_name)
        for _, tag_class in inspect.getmembers(module, is_tag_class):
            module_category.register_tag_class(tag_class)

    def register_tags_in_package(self, package):
        self.log.debug(f"Discovering tags in package '{package}'")

        for _, name, is_pkg in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            if is_pkg:
                continue
            try:
                self.log.debug(f"Trying to load {name} module")
                module = importlib.import_module(name)
                self.register_tags_in_module(module)
            except NotImplementedError as exc:
                self.log.warning(f"Module {name} is currently unsupported: {exc}")
            except Exception as exc:
                self.log.error(exc, f"Could not load module {name}")


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


class ContextMissingError(TagError):
    def __init__(self, tag_name: QualifiedTagName):
        super().__init__(tag_name, f"Context is required for this tag")


class ContextForbiddenError(TagError):
    def __init__(self, tag_name: QualifiedTagName):
        super().__init__(tag_name, f"This tag cannot be used with context")


class ConfigurationError(TagError):
    def __init__(self, tag_name: QualifiedTagName, message: str):
        super().__init__(tag_name, f"Configuration not valid: {message}")


class AliasRegistry:
    log: Logger
    _category_map: Dict[CategoryName, Dict[TagName, Alias]]
    _default_category_name = CategoryName("Aliases")

    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)
        self._category_map = {}

    def aliases(self) -> Iterator[Tuple[QualifiedTagName, Alias]]:
        """Provides view for all stored aliases"""
        for category_name, aliases_in_category in self._category_map.items():
            for alias_name, alias in aliases_in_category.items():
                yield QualifiedTagName(alias_name, category_name), alias

    def register_alias(self, qualified_name: QualifiedTagName, pattern_text: str):
        category_name = qualified_name.category
        if not category_name:
            category_name = AliasRegistry._default_category_name

        if category_name not in self._category_map:
            self.log.debug("Creating category %r", category_name)
            self._category_map[category_name] = {}
        category_tags = self._category_map[category_name]
        if qualified_name.name in category_tags:
            raise ValueError(f"{qualified_name} alias is already registered")
        category_tags[qualified_name.name] = Alias(pattern_text)

    def find_alias(self, qualified_name: QualifiedTagName) -> Optional[Alias]:
        if qualified_name.category:
            if qualified_name.category not in self._category_map:
                self.log.debug("Could not find category %r", qualified_name.category)
                return None
            category_tags = self._category_map[qualified_name.category]
            if qualified_name.name not in category_tags:
                self.log.debug(
                    "Could not find alias %r in category %r",
                    qualified_name.name,
                    qualified_name.category,
                )
                return None
            return category_tags[qualified_name.name]
        else:
            candidate_aliases = list(
                filter(lambda t: t[0].name == qualified_name.name, self.aliases())
            )
            if len(candidate_aliases) != 1:
                categories_with_the_same_name = list(
                    starmap(lambda name, _: name.category, candidate_aliases)
                )
                raise AmbiguousNameError(qualified_name, categories_with_the_same_name)
            return candidate_aliases[0][1]
