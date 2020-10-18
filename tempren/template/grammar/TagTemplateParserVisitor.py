# Generated from TagTemplateParser.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .TagTemplateParser import TagTemplateParser
else:
    from TagTemplateParser import TagTemplateParser

# This class defines a complete generic visitor for a parse tree produced by TagTemplateParser.

class TagTemplateParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TagTemplateParser#pattern.
    def visitPattern(self, ctx:TagTemplateParser.PatternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TagTemplateParser#tag.
    def visitTag(self, ctx:TagTemplateParser.TagContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TagTemplateParser#rawText.
    def visitRawText(self, ctx:TagTemplateParser.RawTextContext):
        return self.visitChildren(ctx)



del TagTemplateParser