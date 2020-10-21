from abc import abstractmethod, ABC
from dataclasses import field, dataclass
from typing import List, Optional, Union, Any, Mapping

from antlr4 import InputStream, CommonTokenStream

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


class _TreeVisitor(TagTemplateParserVisitor):
    def defaultResult(self) -> List[PatternElement]:
        return list()

    def aggregateResult(self, pattern: List[PatternElement], element: Union[PatternElement, List]):
        print("Aggregating", repr(pattern), repr(element))
        if isinstance(element, list):
            return pattern
        return pattern + [element]

    def visitRootPattern(self, ctx: TagTemplateParser.RootPatternContext):
        return self.visitPattern(ctx.pattern())

    def visitPattern(self, ctx: TagTemplateParser.PatternContext):
        print("Visiting pattern: ", ctx.getText())
        pattern_elements = self.visitChildren(ctx)
        return Pattern(pattern_elements)

    def visitTag(self, ctx: TagTemplateParser.TagContext):
        tag_name = ctx.TAG_ID().getText()
        args = self.visitArgumentList(ctx.argumentList())
        ctx.argumentList()
        context: Optional[Pattern] = None
        if ctx.context:
            context = self.visitPattern(ctx.context)
        tag = Tag(tag_name, args=args, context=context)
        return tag

    # def visitArgumentList(self, ctx: TagTemplateParser.ArgumentListContext):
    #     return super().visitArgumentList(ctx)

    def visitArgument(self, ctx: TagTemplateParser.ArgumentContext):
        if ctx.BOOLEAN_ARGUMENT():
            return ctx.BOOLEAN_ARGUMENT().getText() == "true"
        elif ctx.NUMERIC_ARGUMENT():
            return int(ctx.NUMERIC_ARGUMENT().getText())
        return super().visitArgument(ctx)

    def visitRawText(self, ctx: TagTemplateParser.RawTextContext):
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
