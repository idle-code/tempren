# Generated from TagTemplateParser.g4 by ANTLR 4.10.1
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .TagTemplateParser import TagTemplateParser
else:
    from TagTemplateParser import TagTemplateParser

# This class defines a complete generic visitor for a parse tree produced by TagTemplateParser.


class TagTemplateParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TagTemplateParser#rootPattern.
    def visitRootPattern(self, ctx: TagTemplateParser.RootPatternContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by TagTemplateParser#tag.
    def visitTag(self, ctx: TagTemplateParser.TagContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by TagTemplateParser#pipeList.
    def visitPipeList(self, ctx: TagTemplateParser.PipeListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by TagTemplateParser#pattern.
    def visitPattern(self, ctx: TagTemplateParser.PatternContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by TagTemplateParser#argumentList.
    def visitArgumentList(self, ctx: TagTemplateParser.ArgumentListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by TagTemplateParser#argument.
    def visitArgument(self, ctx: TagTemplateParser.ArgumentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by TagTemplateParser#argumentValue.
    def visitArgumentValue(self, ctx: TagTemplateParser.ArgumentValueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by TagTemplateParser#rawText.
    def visitRawText(self, ctx: TagTemplateParser.RawTextContext):
        return self.visitChildren(ctx)


del TagTemplateParser
