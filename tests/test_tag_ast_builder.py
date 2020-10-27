from tempren.template.TagAstBuilder import *


def parse(text: str) -> Pattern:
    ast_builder = TagAstBuilder()
    return ast_builder.parse(text)


class TestAstBuilder:
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

    def test_curly_braces_escaping(self):
        pattern = parse("Text with \\{ braces \\}")

        assert pattern == Pattern([RawText("Text with { braces }")])

    def test_integer_argument(self):
        pattern = parse("%TAG(123)")

        assert pattern == Pattern([Tag("TAG", args=[123])])

    def test_boolean_arguments(self):
        true_pattern = parse("%TRUE(true)")
        capital_true_pattern = parse("%TRUE(True)")
        false_pattern = parse("%FALSE(false)")
        capital_false_pattern = parse("%FALSE(False)")

        true_expected_pattern = Pattern([Tag("TRUE", args=[True])])
        assert true_pattern == true_expected_pattern
        assert capital_true_pattern == true_expected_pattern
        false_expected_pattern = Pattern([Tag("FALSE", args=[False])])
        assert false_pattern == false_expected_pattern
        assert capital_false_pattern == false_expected_pattern

    def test_string_argument(self):
        pattern = parse("%TAG('text value')")

        assert pattern == Pattern([Tag("TAG", args=["text value"])])

    def test_empty_string_argument(self):
        pattern = parse("%TAG('')")

        assert pattern == Pattern([Tag("TAG", args=[""])])

    def test_escape_sequence_in_string_argument(self):
        quote_pattern = parse("%TAG('Don\\'t')")
        backslash_pattern = parse("%TAG('C:\\\\Windows')")

        assert quote_pattern == Pattern([Tag("TAG", args=["Don't"])])
        assert backslash_pattern == Pattern([Tag("TAG", args=["C:\\Windows"])])

    def test_multiple_positional_arguments(self):
        pattern = parse("%TAG(123, true)")

        assert pattern == Pattern([Tag("TAG", args=[123, True])])

    def test_named_arguments(self):
        pattern = parse("%TAG(foo=123, bar='spam', baz=true)")

        assert pattern == Pattern(
            [Tag("TAG", kwargs={"foo": 123, "bar": "spam", "baz": True})]
        )

    def test_mixed_argument_types(self):
        pattern = parse("%TAG(123, bar='spam', true)")

        assert pattern == Pattern(
            [Tag("TAG", args=[123, True], kwargs={"bar": "spam"})]
        )

    # TODO: support string arguments in double quotes


class TestTagAstBuilderErrors:
    pass
