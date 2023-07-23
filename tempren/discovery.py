import importlib
import inspect
import logging
import pkgutil
from collections import defaultdict
from types import ModuleType
from typing import Callable, Dict, List, Type, TypeVar

from tempren.alias import TagAlias
from tempren.primitives import CategoryName, Tag

log = logging.getLogger(__name__)


def discover_tags_in_package(package) -> Dict[CategoryName, List[Type[Tag]]]:
    return _discover_classes_in_package(package, Tag)


def discover_aliases_in_package(package) -> Dict[CategoryName, List[Type[TagAlias]]]:
    return _discover_classes_in_package(package, TagAlias)


BaseClass = TypeVar("BaseClass")


def _discover_classes_in_package(
    package, base_klass: Type[BaseClass]
) -> Dict[CategoryName, List[Type[BaseClass]]]:
    def _is_base_class(klass: type):
        if (
            not inspect.isclass(klass)
            or not issubclass(klass, base_klass)
            or inspect.isabstract(klass)
            or klass == base_klass
        ):
            return False
        return klass.__name__.endswith(base_klass.__name__)

    found_classes = defaultdict(list)

    def _visitor(module: ModuleType, klass: type):
        if not _is_base_class(klass):
            return
        if module.__package__:
            category_name = CategoryName(module.__name__[len(module.__package__) + 1 :])
        else:
            category_name = CategoryName(module.__name__)

        found_classes[category_name].append(klass)

    visit_types_in_package(package, _visitor)

    return found_classes


def visit_types_in_package(
    package: ModuleType, visitor: Callable[[ModuleType, type], None]
):
    log.debug(f"Discovering types in package '{package}'")

    for _, name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        if is_pkg:
            continue
        try:
            log.debug(f"Trying to load {name} module")
            module = importlib.import_module(name)
            visit_types_in_module(module, visitor)
        except NotImplementedError as exc:
            log.warning(f"Module {name} is currently unsupported: {exc}")
        except Exception as exc:
            log.error(exc, f"Could not load module {name}")


def visit_types_in_module(
    module: ModuleType, visitor: Callable[[ModuleType, type], None]
):
    log.debug(f"Discovering types in module '{module}'")

    for _, tag_class in inspect.getmembers(module):
        if isinstance(tag_class, type):
            visitor(module, tag_class)
