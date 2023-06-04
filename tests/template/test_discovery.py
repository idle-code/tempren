import itertools
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from typing import Dict, List

from tempren.discovery import (
    discover_tags_in_package,
    visit_types_in_module,
    visit_types_in_package,
)
from tempren.primitives import CategoryName


class CollectingVisitor:
    found_types: Dict[object, List[type]]

    def __init__(self):
        self.found_types = defaultdict(list)

    def __call__(self, module, klass: type):
        self.found_types[module].append(klass)


class TestTagDiscovery:
    def test_visit_types_in_package__finds_all_classes(self):
        import tests.template.test_module

        type_collector = CollectingVisitor()

        visit_types_in_package(tests.template.test_module, type_collector)

        found_classes = list(itertools.chain(*type_collector.found_types.values()))
        assert tests.template.test_module.first_level.FirstLevelTag in found_classes
        assert tests.template.test_module.first_level.AbstractTag in found_classes
        assert (
            tests.template.test_module.submodule.second_level.SecondLevelTag
            in found_classes
        )

    def test_visit_types_in_module__finds_all_classes(self):
        from .test_module import first_level

        type_collector = CollectingVisitor()

        visit_types_in_module(first_level, type_collector)

        assert len(type_collector.found_types) == 1
        _, classes = list(type_collector.found_types.items())[0]
        assert first_level.FirstLevelTag in classes
        assert first_level.AbstractTag in classes

    def test_visit_types_in_package__skips_unsupported_modules(self):
        import tests.template.test_module

        type_collector = CollectingVisitor()

        visit_types_in_package(tests.template.test_module, type_collector)

        unsupported_module = CategoryName("unsupported_module")
        assert unsupported_module not in type_collector.found_types

        found_class_names = list(
            map(
                lambda t: t.__name__,
                itertools.chain(*type_collector.found_types.values()),
            )
        )
        assert "UnsupportedTag" not in found_class_names

    @staticmethod
    def _load_module_from_path(module_path: Path) -> ModuleType:
        module_name = module_path.stem
        import importlib.util

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_discover_tags_in_package__finds_all_tags(self):
        import tests.template.test_module

        found_tags = discover_tags_in_package(tests.template.test_module)

        first_level_category = CategoryName("first_level")
        assert first_level_category in found_tags
        assert (
            tests.template.test_module.first_level.FirstLevelTag
            in found_tags[first_level_category]
        )

        second_level_category = CategoryName("second_level")
        assert second_level_category in found_tags
        assert (
            tests.template.test_module.submodule.second_level.SecondLevelTag
            in found_tags[second_level_category]
        )

    def test_discover_tags_in_package__doesnt_include_abstract_tags(self):
        import tests.template.test_module

        found_tags = discover_tags_in_package(tests.template.test_module)

        first_level_category = CategoryName("first_level")
        assert first_level_category in found_tags
        assert (
            tests.template.test_module.first_level.AbstractTag
            not in found_tags[first_level_category]
        )
