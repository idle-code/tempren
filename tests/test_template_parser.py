from tempren.template.RawText import RawText
from tempren.template.TagExpression import TagExpression
from tempren.template.TagInvocation import TagInvocation
from tempren.template.TagExpressionParser import TagExpressionParser


def parse(text: str) -> TagExpression:
    from tempren.template.TagExpressionLexer import TagExpressionLexer
    from antlr4 import CommonTokenStream, InputStream

    lexer = TagExpressionLexer(InputStream(text))
    stream = CommonTokenStream(lexer)
    parser = TagExpressionParser(stream)
    pattern = parser.pattern()

    # TODO: create error listener
    # TODO: create listener for creating expression tree?

    return pattern_to_expression(pattern)


Symbol = TagExpressionParser


def pattern_to_expression(pattern) -> TagExpression:
    # FIXME: implement this
    pass
    #return list(map(lambda c: c.symbol.type, pattern.children))


class TestParser:
    def test_just_text(self):
        expression = parse("Just text")

        # TODO: create expr, tag, text shortcuts/aliases
        assert expression == TagExpression([RawText("Just text")])

    def test_just_tag(self):
        expression = parse("%JUST_TAG()")

        assert expression == TagExpression([TagInvocation("JUST_TAG")])
