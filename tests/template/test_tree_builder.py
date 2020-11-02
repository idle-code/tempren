from dataclasses import dataclass

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


@dataclass
class MockTag(Tag):
    args: Tuple[ArgValue, ...]
    kwargs: Mapping[str, ArgValue]

    def __init__(self, *args, context: Optional[Pattern] = None, **kwargs):
        super().__init__(context=context)
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return "Mock output"


class TestTagTreeBinder:
    def test_use_provided_tag_name(self):
        binder = TagTreeBinder()

        binder.register_tag(FakeTag, "FooBar")

        foobar_tag = binder.find_tag("FooBar")
        assert foobar_tag

    def test_generate_name_based_on_class(self):
        binder = TagTreeBinder()

        binder.register_tag(FakeTag)

        fake_tag = binder.find_tag("Fake")
        assert fake_tag

    def test_invalid_tag_class_name(self):
        class FakeExtractor(Tag):
            def __str__(self) -> str:
                pass

        binder = TagTreeBinder()

        with pytest.raises(ValueError):
            binder.register_tag(FakeExtractor)

    def test_register_tag(self):
        binder = TagTreeBinder()

        binder.register_tag(FakeTag)
        found_factory = binder.find_tag("Fake")

        assert found_factory is FakeTag

    def test_register_existing_tag(self):
        binder = TagTreeBinder()
        binder.register_tag(FakeTag)

        with pytest.raises(ValueError):
            binder.register_tag(FakeTag)

    def test_missing_tag(self):
        pattern = parse("%Nonexistent()")
        binder = TagTreeBinder()

        with pytest.raises(UnknownTagError) as exc:
            binder.bind(pattern)

        exc.match("Nonexistent")

    def test_tag_factory_is_invoked(self):
        pattern = parse("%Dummy()")
        binder = TagTreeBinder()
        invoked = False

        def DummyTag(*args, **kwargs):
            nonlocal invoked
            invoked = True
            return MockTag(*args, **kwargs)

        binder.register_tag(DummyTag)

        binder.bind(pattern)

        assert invoked

    def test_placeholder_positional_arguments_are_passed(self):
        pattern = parse("%Dummy(1, 'text', true)")
        binder = TagTreeBinder()
        positional_args = None

        def DummyTag(*args, **kwargs):
            nonlocal positional_args
            positional_args = args
            return MockTag(*args, **kwargs)

        binder.register_tag(DummyTag)

        binder.bind(pattern)

        assert positional_args == (1, "text", True)

    def test_placeholder_keyword_arguments_are_passed(self):
        pattern = parse("%Dummy(a=1, b='text', c=true)")
        binder = TagTreeBinder()
        keyword_args = None

        def DummyTag(*args, context: Optional[Pattern], **kwargs):
            nonlocal keyword_args
            keyword_args = kwargs
            return MockTag(*args, **kwargs)

        binder.register_tag(DummyTag)

        binder.bind(pattern)

        assert keyword_args == {"a": 1, "b": "text", "c": True}

    def test_context_present_information_is_passed(self):
        pattern = parse("%Dummy(){test}")
        binder = TagTreeBinder()
        is_context_present = None

        def DummyTag(*args, context: Optional[Pattern], **kwargs):
            nonlocal is_context_present
            is_context_present = context is not None
            return MockTag(*args, **kwargs)

        binder.register_tag(DummyTag)

        binder.bind(pattern)

        assert is_context_present

    def test_context_pattern_is_rewritten(self):
        pattern = parse("%Outer(name='outer'){%Inner(name='inner')}")
        binder = TagTreeBinder()
        binder.register_tag(MockTag, "Outer")
        binder.register_tag(MockTag, "Inner")

        bound_pattern = binder.bind(pattern)

        inner_tag = MockTag(name="inner")
        outer_tag = MockTag(name="outer")
        outer_tag.context = Pattern([inner_tag])
        assert bound_pattern == Pattern([outer_tag])

    def test_raw_text_is_rewritten(self):
        pattern = parse("Just text")
        binder = TagTreeBinder()

        bound_pattern = binder.bind(pattern)

        assert bound_pattern == Pattern([RawText("Just text")])
