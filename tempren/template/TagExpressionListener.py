# Generated from TagExpression.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .TagExpressionParser import TagExpressionParser
else:
    from TagExpressionParser import TagExpressionParser

# This class defines a complete listener for a parse tree produced by TagExpressionParser.
class TagExpressionListener(ParseTreeListener):

    # Enter a parse tree produced by TagExpressionParser#pattern.
    def enterPattern(self, ctx:TagExpressionParser.PatternContext):
        pass

    # Exit a parse tree produced by TagExpressionParser#pattern.
    def exitPattern(self, ctx:TagExpressionParser.PatternContext):
        pass


    # Enter a parse tree produced by TagExpressionParser#tag.
    def enterTag(self, ctx:TagExpressionParser.TagContext):
        pass

    # Exit a parse tree produced by TagExpressionParser#tag.
    def exitTag(self, ctx:TagExpressionParser.TagContext):
        pass



del TagExpressionParser