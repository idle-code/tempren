# Generated from TagTemplateParser.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .TagTemplateParser import TagTemplateParser
else:
    from TagTemplateParser import TagTemplateParser

# This class defines a complete listener for a parse tree produced by TagTemplateParser.
class TagTemplateParserListener(ParseTreeListener):

    # Enter a parse tree produced by TagTemplateParser#pattern.
    def enterPattern(self, ctx:TagTemplateParser.PatternContext):
        pass

    # Exit a parse tree produced by TagTemplateParser#pattern.
    def exitPattern(self, ctx:TagTemplateParser.PatternContext):
        pass


    # Enter a parse tree produced by TagTemplateParser#tag.
    def enterTag(self, ctx:TagTemplateParser.TagContext):
        pass

    # Exit a parse tree produced by TagTemplateParser#tag.
    def exitTag(self, ctx:TagTemplateParser.TagContext):
        pass


    # Enter a parse tree produced by TagTemplateParser#argumentList.
    def enterArgumentList(self, ctx:TagTemplateParser.ArgumentListContext):
        pass

    # Exit a parse tree produced by TagTemplateParser#argumentList.
    def exitArgumentList(self, ctx:TagTemplateParser.ArgumentListContext):
        pass


    # Enter a parse tree produced by TagTemplateParser#tagContext.
    def enterTagContext(self, ctx:TagTemplateParser.TagContextContext):
        pass

    # Exit a parse tree produced by TagTemplateParser#tagContext.
    def exitTagContext(self, ctx:TagTemplateParser.TagContextContext):
        pass


    # Enter a parse tree produced by TagTemplateParser#rawText.
    def enterRawText(self, ctx:TagTemplateParser.RawTextContext):
        pass

    # Exit a parse tree produced by TagTemplateParser#rawText.
    def exitRawText(self, ctx:TagTemplateParser.RawTextContext):
        pass



del TagTemplateParser