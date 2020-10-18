from abc import abstractmethod, ABC
from dataclasses import field, dataclass
from typing import List, Optional, Union

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

    def __str__(self) -> str:
        return f"%{self.tag_name}()"


class _TreeVisitor(TagTemplateParserVisitor):
    def defaultResult(self) -> List[PatternElement]:
        return list()

    def aggregateResult(self, pattern: List[PatternElement], element: Union[PatternElement, List]):
        print("Aggregating", repr(pattern), repr(element))
        if isinstance(element, list):
            return pattern
        return pattern + [element]

    def visitRootPattern(self, ctx: TagTemplateParser.RootPatternContext):
        return self.visitPattern(ctx)

    def visitPattern(self, ctx: TagTemplateParser.PatternContext):
        print("Visiting pattern: ", ctx.getText())
        pattern_elements = self.visitChildren(ctx)
        return Pattern(pattern_elements)

    def visitTag(self, ctx: TagTemplateParser.TagContext):
        context: List[Pattern] = self.visitChildren(ctx)
        tag_name = ctx.TAG_ID().getText()
        if context:
            assert len(context) == 1
            tag = Tag(tag_name, context=context[0])
        else:
            tag = Tag(tag_name)
        return tag

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
        root_pattern = visitor.visitRootPattern(parser.pattern())
        return root_pattern
