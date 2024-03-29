import pytest

from tempren.template.exceptions import TemplateSemanticError
from tempren.template.parser import *

from ..conftest import pattern_from


def parse(text: str) -> Pattern:
    ast_builder = TemplateParser()
    return ast_builder.parse(text)


class TestParser:
    def test_empty(self):
        pattern = parse("")

        assert pattern == pattern_from()

    def test_just_text(self):
        pattern = parse("Just text")

        assert pattern == pattern_from(RawText("Just text"))

    def test_just_tag(self):
        pattern = parse("%JUST_TAG()")

        assert pattern == pattern_from(TagPlaceholder(QualifiedTagName("JUST_TAG")))

    def test_category_prefixed_tag(self):
        pattern = parse("%CATEGORY.TAG()")

        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG", "CATEGORY"))
        )

    def test_text_and_tag(self):
        pattern = parse("Text with a %TAG()")

        assert pattern == pattern_from(
            RawText("Text with a "), TagPlaceholder(QualifiedTagName("TAG"))
        )

    def test_tag_with_text_context(self):
        pattern = parse("%TAG(){Context text}")

        tag_context = pattern_from(RawText("Context text"))
        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), context=tag_context)
        )

    def test_tag_with_tag_context(self):
        pattern = parse("%TAG(){Context %SUB_TAG()}")

        tag_context = pattern_from(
            RawText("Context "), TagPlaceholder(QualifiedTagName("SUB_TAG"))
        )
        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), context=tag_context)
        )

    def test_tag_with_just_tag_context(self):
        pattern = parse("%TAG{Context text}")

        tag_context = pattern_from(RawText("Context text"))
        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), context=tag_context)
        )

    def test_parenthesis_escaping(self):
        pattern = parse("Text with (parentheses)")

        assert pattern == pattern_from(RawText("Text with (parentheses)"))

    def test_curly_braces_escaping(self):
        pattern = parse("Text with \\{ braces \\}")

        assert pattern == pattern_from(RawText("Text with { braces }"))

    @pytest.mark.skip("Not tested yet")
    def test_curly_braces_no_tag_no_escaping(self):
        pattern = parse("Text with { braces }")

        assert pattern == pattern_from(RawText("Text with { braces }"))

    def test_numeric_argument(self):
        pattern = parse("%TAG(123)")

        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=[123])
        )

    def test_negative_numeric_argument(self):
        pattern = parse("%TAG(-123)")

        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=[-123])
        )

    def test_boolean_arguments(self):
        true_pattern = parse("%TRUE(true)")
        false_pattern = parse("%FALSE(false)")

        assert true_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TRUE"), args=[True])
        )
        assert false_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("FALSE"), args=[False])
        )

    def test_boolean_capital_arguments(self):
        capital_true_pattern = parse("%TRUE(True)")
        capital_false_pattern = parse("%FALSE(False)")

        assert capital_true_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TRUE"), args=[True])
        )
        assert capital_false_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("FALSE"), args=[False])
        )

    def test_boolean_flag(self):
        bool_flag_pattern = parse("%TAG(flag_name)")

        assert bool_flag_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), kwargs={"flag_name": True})
        )

    def test_string_argument(self):
        pattern = parse("%TAG('text value')")

        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=["text value"])
        )

    def test_double_quoted_string_argument(self):
        pattern = parse('%TAG("quoted value")')

        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=["quoted value"])
        )

    def test_empty_string_argument(self):
        pattern = parse("%TAG('')")

        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=[""])
        )

    def test_escape_sequence_in_string_argument(self):
        quote_pattern = parse("%TAG('Don\\'t')")
        backslash_pattern = parse("%TAG('C:\\\\Windows')")

        assert quote_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=["Don't"])
        )
        assert backslash_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=["C:\\Windows"])
        )

    def test_invalid_escape_sequence_in_string_argument(self):
        quote_pattern = parse("%TAG('Quote: \"')")
        escaped_quote_pattern = parse("%TAG('Quote: \\\"')")

        assert quote_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=['Quote: "'])
        )
        assert escaped_quote_pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=['Quote: \\"'])
        )

    def test_multiple_positional_arguments(self):
        pattern = parse("%TAG(123, true)")

        assert pattern == pattern_from(
            TagPlaceholder(QualifiedTagName("TAG"), args=[123, True])
        )

    def test_named_arguments(self):
        pattern = parse("%TAG(foo=123, bar='spam', baz=true)")

        assert pattern == pattern_from(
            TagPlaceholder(
                QualifiedTagName("TAG"),
                kwargs={"foo": 123, "bar": "spam", "baz": True},
            )
        )

    def test_mixed_argument_types(self):
        pattern = parse("%TAG(123, bar='spam', true)")

        assert pattern == pattern_from(
            TagPlaceholder(
                QualifiedTagName("TAG"), args=[123, True], kwargs={"bar": "spam"}
            )
        )

    def test_single_pipe(self):
        pattern = parse("Text|%TAG()")
        equivalent_pattern = parse("%TAG(){Text}")

        assert pattern == equivalent_pattern

    def test_multiple_tags_in_pipe(self):
        pattern = parse("%First()|%Second()|%Third()")
        equivalent_pattern = parse("%Third(){%Second(){%First()}}")

        assert pattern == equivalent_pattern

    def test_pipe_symbol_escaping(self):
        pattern = parse("Text\\|pipe")

        assert pattern == pattern_from(RawText("Text|pipe"))

    def test_pipe_as_tag_context(self):
        pattern = parse("%OUTER(){Text|%INNER()}")
        equivalent_pattern = parse("%OUTER(){%INNER(){Text}}")

        assert pattern == equivalent_pattern


class TestParserSyntaxErrors:
    def test_missing_closing_argument_bracket(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %TAG( text")

        assert "missing closing" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 9, 1)

    def test_missing_closing_argument_bracket_at_end(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %TAG(")

        assert "missing closing" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 9, 1)

    def test_missing_opening_argument_bracket(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %TAG text)")

        assert "unexpected symbol 'text'" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 10, 4)

    def test_missing_opening_argument_bracket_at_end(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %TAG")

        assert "missing argument list" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 6, 3)

    def test_missing_closing_context_bracket(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %TAG(){ Context")

        assert "missing closing context bracket" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 11, 1)

    def test_missing_closing_context_bracket_no_argument_list(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %TAG{ Context")

        assert "missing closing context bracket" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 9, 1)

    def test_unescaped_context_opening_bracket(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some { Context ")

        assert "unexpected symbol '{'" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 5, 1)

    def test_unescaped_context_closing_bracket(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %TAG() Context }")

        assert "unexpected symbol '}'" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 20, 1)

    def test_missing_tag_name(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %()")

        assert "missing tag" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 5, 1)

    def test_missing_tag_name_with_context(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %{Context}")

        assert "missing tag" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 5, 1)

    def test_missing_tag_category(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Some %.TAG()")

        assert "missing category" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 6, 1)

    def test_non_tag_in_pipe_list(self):
        with pytest.raises(TemplateSyntaxError) as syntax_error:
            parse("Text|Pipe")

        assert "non-tag in the pipe list" in syntax_error.value.message
        assert syntax_error.value.location == Location(1, 5, 4)


class TestParserSemanticErrors:
    @pytest.mark.skip("Might not be an error")
    def test_empty_context(self):
        with pytest.raises(TemplateSemanticError) as semantic_error:
            parse("%TAG(){}")

        # assert "unescaped context bracket" in syntax_error.value.message
        # assert syntax_error.value.location == Location(1, 6, 1)
