from abc import abstractmethod, ABC
from dataclasses import field, dataclass
from typing import List, Optional

from antlr4 import ParseTreeWalker

from .grammar.TagTemplateLexer import TagTemplateLexer, CommonTokenStream
from .grammar.TagTemplateParser import TagTemplateParser
from .grammar.TagTemplateParserListener import TagTemplateParserListener, InputStream
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
    root_pattern: Pattern = None
    current_pattern: Pattern = None

    def visitPattern(self, ctx: TagTemplateParser.PatternContext):
        print("Visiting pattern:", ctx)
        self.current_pattern = Pattern()
        if not self.root_pattern:
            self.root_pattern = self.current_pattern
        self.visitChildren(ctx)
        return self.current_pattern

    def visitTag(self, ctx: TagTemplateParser.TagContext):
        print("Visiting tag:", ctx)
        assert self.current_pattern
        tag = Tag(ctx.TAG_ID().getText())
        self.current_pattern.sub_elements.append(tag)
        return tag

    def visitRawText(self, ctx: TagTemplateParser.RawTextContext):
        print("Visiting raw text:", ctx)
        assert self.current_pattern
        raw_text = RawText(ctx.TEXT().getText())
        self.current_pattern.sub_elements.append(raw_text)
        return raw_text


class TagTreeBuilder:
    def parse(self, text: str) -> Pattern:
        lexer = TagTemplateLexer(InputStream(text))
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = TagTemplateParser(token_stream)

        visitor = _TreeVisitor()
        visitor.visitPattern(parser.pattern())
        return visitor.root_pattern
