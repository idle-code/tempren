from typing import Optional

import pytest
from tempren.template.tags import TagFactory
from tempren.template.tree_elements import Tag


class MockTag(Tag):
    def __init__(
        self,
        *args,
        context_present: bool = False,
        output: Optional[str] = None,
        **kwargs
    ):
        self.args = args
        self.kwargs = kwargs
        self.context_present = context_present
        self.output = output

    def __str__(self) -> str:
        return self.output


class TestTagFactory:
    def test_use_provided_tag_name(self):
        class DemoTag(Tag):
            pass

        factory = TagFactory(DemoTag, "FooBar")

        assert factory.tag_name == "FooBar"

    def test_generate_name_based_on_class(self):
        class DemoTag(Tag):
            pass

        factory = TagFactory(DemoTag)

        assert factory.tag_name == "Demo"

    def test_invalid_tag_class_name(self):
        class DummyExtension(Tag):
            pass

        with pytest.raises(ValueError):
            TagFactory(DummyExtension)

    def test_register_factory(self):
        factory = TagFactory(MockTag)

    def test_create_instance_passes_args(self):
        factory = TagFactory(MockTag)

        tag_mock: MockTag = factory.create_instance(True, 1, 2, 3, test="string")

        assert tag_mock.args == (1, 2, 3)
        assert tag_mock.kwargs == {"test": "string"}
        assert tag_mock.context_present
