from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Tuple, Union

from antlr4 import CommonTokenStream, InputStream

from .grammar.TagTemplateLexer import TagTemplateLexer
from .grammar.TagTemplateParser import TagTemplateParser
from .grammar.TagTemplateParserVisitor import TagTemplateParserVisitor


class PatternElement(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass
class Pattern(PatternElement):
    sub_elements: List[PatternElement] = field(default_factory=list)

    def __str__(self) -> str:
        return "".join(map(str, self.sub_elements))


@dataclass
class RawText(PatternElement):
    text: str

    def __str__(self) -> str:
        return self.text


@dataclass
class Tag(PatternElement):
    tag_name: str
    context: Optional[Pattern] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"%{self.tag_name}({self.args})"


ArgValue = Union[str, int, bool]


class _TreeVisitor(TagTemplateParserVisitor):
    def defaultResult(self) -> List[PatternElement]:
        return list()

    def aggregateResult(
        self, pattern: List[PatternElement], element: Union[PatternElement, List]
    ):
        if isinstance(element, list):
            return pattern
        return pattern + [element]

    def visitRootPattern(self, ctx: TagTemplateParser.RootPatternContext):
        return self.visitPattern(ctx.pattern())

    def visitPattern(self, ctx: TagTemplateParser.PatternContext):
        pattern_elements = self.visitChildren(ctx)
        return Pattern(pattern_elements)

    def visitTag(self, ctx: TagTemplateParser.TagContext):
        tag_name = ctx.TAG_ID().getText()
        args, kwargs = self.visitArgumentList(ctx.argumentList())
        ctx.argumentList()
        context: Optional[Pattern] = None
        if ctx.context:
            context = self.visitPattern(ctx.context)
        tag = Tag(tag_name, args=args, kwargs=kwargs, context=context)
        return tag

    def visitArgumentList(
        self, ctx: TagTemplateParser.ArgumentListContext
    ) -> Tuple[List[ArgValue], Mapping[str, ArgValue]]:
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
            if str_val == "''":
                return ""
            return self._unescape(str_val)
        raise NotImplementedError("Unknown argument value token: " + ctx.getText())

    def _unescape(self, text: str) -> str:
        return text.replace("\\'", "'").replace("\\\\", "\\")

    def visitArgument(
        self, ctx: TagTemplateParser.ArgumentContext
    ) -> Tuple[Optional[str], ArgValue]:
        arg_value = self.visitArgumentValue(ctx.argumentValue())
        arg_name = None
        if ctx.ARG_NAME():
            arg_name = ctx.ARG_NAME().getText()
        return arg_name, arg_value

    def visitRawText(self, ctx: TagTemplateParser.RawTextContext) -> RawText:
        raw_text = RawText(ctx.TEXT().getText())
        return raw_text


class TagTreeBuilder:
    def parse(self, text: str) -> Pattern:
        lexer = TagTemplateLexer(InputStream(text))
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = TagTemplateParser(token_stream)

        visitor = _TreeVisitor()
        root_pattern = visitor.visitRootPattern(parser.rootPattern())
        return root_pattern
