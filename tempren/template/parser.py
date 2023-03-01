import logging
from functools import reduce
from typing import List, Mapping, Optional, Tuple, Union

from antlr4 import CommonTokenStream, InputStream  # type: ignore
from antlr4.error.ErrorListener import ErrorListener  # type: ignore

from tempren.primitives import Location, QualifiedTagName, TagName

from .ast import Pattern, PatternElement, RawText, TagPlaceholder
from .exceptions import TemplateSyntaxError
from .grammar.TagTemplateLexer import TagTemplateLexer
from .grammar.TagTemplateParser import TagTemplateParser
from .grammar.TagTemplateParserVisitor import TagTemplateParserVisitor

ArgValue = Union[str, int, bool]


escaped_characters = ("'", "\\", "{", "}", "|")
replacements = list(("\\" + ec, ec) for ec in escaped_characters)


def unescape(text: str) -> str:
    return reduce(
        lambda acc, replacement: acc.replace(*replacement), replacements, text
    )


IGNORED_TERMINAL = object()
ARGUMENT_VALUE_TYPES = (
    TagTemplateLexer.NUMERIC_VALUE,
    TagTemplateLexer.BOOLEAN_VALUE,
    TagTemplateLexer.STRING_VALUE,
)


def location_from_symbol(symbol) -> Location:
    return Location(
        line=symbol.line, column=symbol.start, length=symbol.stop - symbol.start + 1
    )


def merge_locations(first: Optional[Location], second: Location) -> Location:
    if not first:
        return second
    assert first.line == second.line
    return Location(
        first.line, first.column, second.column + second.length - first.column
    )


class _TreeVisitor(TagTemplateParserVisitor):
    def defaultResult(self) -> List[PatternElement]:
        return list()

    def visitTerminal(self, node):
        if node.getSymbol().type not in ARGUMENT_VALUE_TYPES:
            return IGNORED_TERMINAL
        raise NotImplementedError()

    def aggregateResult(
        self, pattern: List[PatternElement], element: PatternElement
    ) -> List[PatternElement]:
        if element is IGNORED_TERMINAL:
            return pattern
        return pattern + [element]

    def visitRootPattern(self, ctx: TagTemplateParser.RootPatternContext) -> Pattern:
        return self.visitPattern(ctx.pattern())

    def visitPipeList(
        self, ctx: TagTemplateParser.PipeListContext
    ) -> List[TagPlaceholder]:
        if ctx.errorNonTagInPipeList:
            non_tag_symbol = ctx.errorNonTagInPipeList.children[0].symbol
            raise TemplateSyntaxError(
                message=f"non-tag in the pipe list"
            ).with_location(location_from_symbol(non_tag_symbol))
        tag_list = self.visitChildren(ctx)
        return list(filter(bool, tag_list))

    def visitPattern(self, ctx: TagTemplateParser.PatternContext) -> Pattern:
        pattern_elements = self.visitChildren(ctx)
        pipe_list = ctx.pipeList()
        if pipe_list:
            pipe_tags = self.visitPipeList(pipe_list)
            context = Pattern(pattern_elements[:-1])
            for tag_placeholder in pipe_tags:
                tag_placeholder.context = context
                context = Pattern([tag_placeholder])
            return context
        return Pattern(pattern_elements)

    def visitTag(self, ctx: TagTemplateParser.TagContext) -> TagPlaceholder:
        category_name = None
        if ctx.categoryId:
            category_name = ctx.categoryId.text
        if ctx.errorMissingTagId:
            raise TemplateSyntaxError(message=f"missing tag name").with_location(
                location_from_symbol(ctx.errorMissingTagId)
            )
        if ctx.errorMissingCategoryId:
            raise TemplateSyntaxError(message=f"missing category name").with_location(
                location_from_symbol(ctx.errorMissingCategoryId)
            )
        if ctx.errorNoArgumentList:
            raise TemplateSyntaxError(
                message=f"missing argument list for tag '{ctx.errorNoArgumentList.text}'"
            ).with_location(location_from_symbol(ctx.errorNoArgumentList))
        tag_name = TagName(ctx.tagId.text)  # type: ignore
        if ctx.errorUnclosedContext:
            raise TemplateSyntaxError(
                message=f"missing closing context bracket for tag '{tag_name}'"
            ).with_location(location_from_symbol(ctx.errorUnclosedContext))
        args, kwargs = self.visitArgumentList(ctx.argumentList())
        context = None
        context_pattern = ctx.pattern()
        if context_pattern is not None:
            context = self.visitPattern(ctx.pattern())

        tag = TagPlaceholder(
            tag_name=QualifiedTagName(tag_name, category_name),
            args=args,
            kwargs=kwargs,
            context=context,
        )

        tag_name_location = location_from_symbol(ctx.tagId)
        if ctx.categoryId:
            tag_category_location = location_from_symbol(ctx.categoryId)
            tag.location = merge_locations(tag_category_location, tag_name_location)
        else:
            tag.location = tag_name_location
        return tag

    def visitArgumentList(
        self, ctx: TagTemplateParser.ArgumentListContext
    ) -> Tuple[List[ArgValue], Mapping[str, ArgValue]]:
        if ctx is None:
            return [], {}
        if ctx.errorUnclosedArgumentList:
            raise TemplateSyntaxError(
                message="missing closing argument list bracket"
            ).with_location(location_from_symbol(ctx.errorUnclosedArgumentList))
        collected_arguments = super().visitArgumentList(ctx)
        args = [
            arg_val for arg_name, arg_val in collected_arguments if arg_name is None
        ]
        kwargs = {
            arg_name: arg_val
            for arg_name, arg_val in collected_arguments
            if arg_name is not None
        }
        return args, kwargs

    def visitArgumentValue(
        self, ctx: TagTemplateParser.ArgumentValueContext
    ) -> ArgValue:
        if ctx.BOOLEAN_VALUE():
            return ctx.BOOLEAN_VALUE().getText().lower() == "true"
        elif ctx.NUMERIC_VALUE():
            return int(ctx.NUMERIC_VALUE().getText())
        elif ctx.STRING_VALUE():
            str_val = ctx.STRING_VALUE().getText()
            assert len(str_val) >= 2
            str_val = str_val[1:-1]
            return unescape(str_val)
        raise NotImplementedError("Unknown argument value token: " + ctx.getText())

    def visitArgument(
        self, ctx: TagTemplateParser.ArgumentContext
    ) -> Tuple[Optional[str], ArgValue]:
        arg_name = ctx.ARG_NAME().getText() if ctx.ARG_NAME() else None
        if ctx.argumentValue():
            arg_value = self.visitArgumentValue(ctx.argumentValue())
        else:
            arg_value = True
        return arg_name, arg_value

    def visitRawText(self, ctx: TagTemplateParser.RawTextContext) -> RawText:
        symbol = ctx.TEXT().getSymbol()
        # CHECK: is location necessary for RawText?
        raw_text = RawText(text=unescape(ctx.TEXT().getText()))
        raw_text.location = location_from_symbol(symbol)
        return raw_text


class TemplateParser:
    log: logging.Logger

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def parse(self, text: str) -> Pattern:
        self.log.debug("Parsing '%s'", text)
        lexer = TagTemplateLexer(InputStream(text))
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = TagTemplateParser(token_stream)
        parser.addErrorListener(TagTemplateErrorListener())

        visitor = _TreeVisitor()
        root_pattern = visitor.visitRootPattern(parser.rootPattern())
        root_pattern.source_representation = text
        return root_pattern


class TagTemplateErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_location = Location(line, column, len(offendingSymbol.text))
        if "extraneous input" in msg or "mismatched input" in msg:
            raise TemplateSyntaxError(
                f"unexpected symbol '{offendingSymbol.text}'"
            ).with_location(error_location)
        else:
            raise TemplateSyntaxError(msg).with_location(error_location)
