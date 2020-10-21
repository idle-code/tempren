from tempren.template.TagTreeBuilder import *


def parse(text: str) -> Pattern:
    tree_builder = TagTreeBuilder()
    return tree_builder.parse(text)


class TestTagTreeBuilder:
    def test_empty(self):
        pattern = parse("")

        assert pattern == Pattern()

    def test_just_text(self):
        pattern = parse("Just text")

        assert pattern == Pattern([RawText("Just text")])

    def test_just_tag(self):
        pattern = parse("%JUST_TAG()")

        assert pattern == Pattern([Tag("JUST_TAG")])

    def test_text_and_tag(self):
        pattern = parse("Text with a %TAG()")

        assert pattern == Pattern([RawText("Text with a "), Tag("TAG")])

    def test_tag_with_text_context(self):
        pattern = parse("%TAG(){Context text}")

        tag_context = Pattern([RawText("Context text")])
        assert pattern == Pattern([Tag("TAG", context=tag_context)])

    def test_tag_with_tag_context(self):
        pattern = parse("%TAG(){Context %SUB_TAG()}")

        tag_context = Pattern([RawText("Context "), Tag("SUB_TAG")])
        assert pattern == Pattern([Tag("TAG", context=tag_context)])

    # def test_integer_tag_argument(self):
    #     pattern = parse("%TAG(123)")
    #
    #     assert pattern == Pattern([Tag("TAG", args=[123])])

    # TODO: test argument lists
    # TODO: test escape sequences


class TestTagTreeBuilderErrors:
    pass
