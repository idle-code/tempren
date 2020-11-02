import pytest
from tempren.template.tree_builder import *
from tempren.template.tree_elements import Pattern, RawText, TagPlaceholder


def parse(text: str) -> Pattern:
    ast_builder = TagTreeBuilder()
    return ast_builder.parse(text)


class TestTreeBuilder:
    def test_empty(self):
        pattern = parse("")

        assert pattern == Pattern()

    def test_just_text(self):
        pattern = parse("Just text")

        assert pattern == Pattern([RawText("Just text")])

    def test_just_tag(self):
        pattern = parse("%JUST_TAG()")

        assert pattern == Pattern([TagPlaceholder("JUST_TAG")])

    def test_text_and_tag(self):
        pattern = parse("Text with a %TAG()")

        assert pattern == Pattern([RawText("Text with a "), TagPlaceholder("TAG")])

    def test_tag_with_text_context(self):
        pattern = parse("%TAG(){Context text}")

        tag_context = Pattern([RawText("Context text")])
        assert pattern == Pattern([TagPlaceholder("TAG", context=tag_context)])

    def test_tag_with_tag_context(self):
        pattern = parse("%TAG(){Context %SUB_TAG()}")

        tag_context = Pattern([RawText("Context "), TagPlaceholder("SUB_TAG")])
        assert pattern == Pattern([TagPlaceholder("TAG", context=tag_context)])

    def test_curly_braces_escaping(self):
        pattern = parse("Text with \\{ braces \\}")

        assert pattern == Pattern([RawText("Text with { braces }")])

    def test_numeric_argument(self):
        pattern = parse("%TAG(123)")

        assert pattern == Pattern([TagPlaceholder("TAG", args=[123])])

    def test_negative_numeric_argument(self):
        pattern = parse("%TAG(-123)")

        assert pattern == Pattern([TagPlaceholder("TAG", args=[-123])])

    def test_boolean_arguments(self):
        true_pattern = parse("%TRUE(true)")
        false_pattern = parse("%FALSE(false)")

        assert true_pattern == Pattern([TagPlaceholder("TRUE", args=[True])])
        assert false_pattern == Pattern([TagPlaceholder("FALSE", args=[False])])

    def test_boolean_capital_arguments(self):
        capital_true_pattern = parse("%TRUE(True)")
        capital_false_pattern = parse("%FALSE(False)")

        assert capital_true_pattern == Pattern([TagPlaceholder("TRUE", args=[True])])
        assert capital_false_pattern == Pattern([TagPlaceholder("FALSE", args=[False])])

    def test_string_argument(self):
        pattern = parse("%TAG('text value')")

        assert pattern == Pattern([TagPlaceholder("TAG", args=["text value"])])

    def test_double_quoted_string_argument(self):
        pattern = parse('%TAG("quoted value")')

        assert pattern == Pattern([TagPlaceholder("TAG", args=["quoted value"])])

    def test_empty_string_argument(self):
        pattern = parse("%TAG('')")

        assert pattern == Pattern([TagPlaceholder("TAG", args=[""])])

    def test_escape_sequence_in_string_argument(self):
        quote_pattern = parse("%TAG('Don\\'t')")
        backslash_pattern = parse("%TAG('C:\\\\Windows')")

        assert quote_pattern == Pattern([TagPlaceholder("TAG", args=["Don't"])])
        assert backslash_pattern == Pattern(
            [TagPlaceholder("TAG", args=["C:\\Windows"])]
        )

    def test_invalid_escape_sequence_in_string_argument(self):
        quote_pattern = parse("%TAG('Quote: \"')")
        escaped_quote_pattern = parse("%TAG('Quote: \\\"')")

        assert quote_pattern == Pattern([TagPlaceholder("TAG", args=['Quote: "'])])
        assert escaped_quote_pattern == Pattern(
            [TagPlaceholder("TAG", args=['Quote: \\"'])]
        )

    def test_multiple_positional_arguments(self):
        pattern = parse("%TAG(123, true)")

        assert pattern == Pattern([TagPlaceholder("TAG", args=[123, True])])

    def test_named_arguments(self):
        pattern = parse("%TAG(foo=123, bar='spam', baz=true)")

        assert pattern == Pattern(
            [TagPlaceholder("TAG", kwargs={"foo": 123, "bar": "spam", "baz": True})]
        )

    def test_mixed_argument_types(self):
        pattern = parse("%TAG(123, bar='spam', true)")

        assert pattern == Pattern(
            [TagPlaceholder("TAG", args=[123, True], kwargs={"bar": "spam"})]
        )


class TestTreeBuilderErrors:
    pass


class FakeTag(Tag):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self) -> str:
        return "Fake output"


class TagFactoryMock(TagFactory):
    context_present: bool
    args: Tuple[ArgValue]
    kwargs: Dict[str, ArgValue]

    def __init__(self, tag_class=FakeTag, tag_name=None):
        super().__init__(tag_class, tag_name)

    def create_instance(self, context_present: bool, *args: ArgValue, **kwargs) -> Tag:
        self.context_present = context_present
        self.args = args
        self.kwargs = kwargs
        return self.tag_class(context_present=context_present, *args, **kwargs)


class TestTagTreeBinder:
    def test_register_tag(self):
        binder = TagTreeBinder()
        factory = TagFactory(FakeTag)

        binder.register_tag(factory)
        found_factory = binder.find_tag("Fake")

        assert found_factory is factory

    def test_register_existing_tag(self):
        binder = TagTreeBinder()
        factory = TagFactory(FakeTag)
        binder.register_tag(factory)

        with pytest.raises(ValueError):
            binder.register_tag(factory)

    def test_missing_tag(self):
        pattern = parse("%UNKNOWN_TAG()")
        binder = TagTreeBinder()

        with pytest.raises(UnknownTagError) as exc:
            binder.bind(pattern)

        exc.match("UNKNOWN_TAG")

    def test_tag_factory_is_invoked(self):
        pattern = parse("%TAG()")
        binder = TagTreeBinder()
        mock_factory = TagFactoryMock(FakeTag, "TAG")
        binder.register_tag(mock_factory)

        binder.bind(pattern)

        assert mock_factory.args == ()
        assert mock_factory.kwargs == {}
