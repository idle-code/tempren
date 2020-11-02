from functools import reduce
from typing import Dict, List, Mapping, Optional, Tuple, Union

from antlr4 import CommonTokenStream, InputStream  # type: ignore

from .grammar.TagTemplateLexer import TagTemplateLexer
from .grammar.TagTemplateParser import TagTemplateParser
from .grammar.TagTemplateParserVisitor import TagTemplateParserVisitor
from .tree_elements import (
    Pattern,
    PatternElement,
    RawText,
    Tag,
    TagFactory,
    TagPlaceholder,
)

ArgValue = Union[str, int, bool]


escaped_characters = ("'", "\\", "{", "}")
replacements = list(("\\" + ec, ec) for ec in escaped_characters)


def unescape(text: str) -> str:
    return reduce(
        lambda acc, replacement: acc.replace(*replacement), replacements, text
    )


class _TreeVisitor(TagTemplateParserVisitor):
    def defaultResult(self) -> List[PatternElement]:
        return list()

    def aggregateResult(
        self, pattern: List[PatternElement], element: PatternElement
    ) -> List[PatternElement]:
        return pattern + [element]

    def visitRootPattern(self, ctx: TagTemplateParser.RootPatternContext) -> Pattern:
        return self.visitPattern(ctx.pattern())

    def visitPattern(self, ctx: TagTemplateParser.PatternContext) -> Pattern:
        pattern_elements = self.visitChildren(ctx)
        return Pattern(pattern_elements)

    def visitTag(self, ctx: TagTemplateParser.TagContext) -> TagPlaceholder:
        tag_name = ctx.TAG_ID().getText()
        args, kwargs = self.visitArgumentList(ctx.argumentList())
        ctx.argumentList()
        context: Optional[Pattern] = None
        if ctx.context:
            context = self.visitPattern(ctx.context)
        tag = TagPlaceholder(tag_name, args=args, kwargs=kwargs, context=context)
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
            assert len(str_val) >= 2
            str_val = str_val[1:-1]
            return unescape(str_val)
        raise NotImplementedError("Unknown argument value token: " + ctx.getText())

    def visitArgument(
        self, ctx: TagTemplateParser.ArgumentContext
    ) -> Tuple[Optional[str], ArgValue]:
        arg_name = ctx.ARG_NAME().getText() if ctx.ARG_NAME() else None
        arg_value = self.visitArgumentValue(ctx.argumentValue())
        return arg_name, arg_value

    def visitRawText(self, ctx: TagTemplateParser.RawTextContext) -> RawText:
        raw_text = RawText(unescape(ctx.TEXT().getText()))
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


class UnknownTagError(Exception):
    tag_name: str

    def __init__(self, tag_name: str):
        assert tag_name
        self.tag_name = tag_name
        super().__init__(f"Unknown tag: {self.tag_name}")


class TagTreeBinder:
    tag_registry: Dict[str, TagFactory]

    def __init__(self):
        self.tag_registry = {}

    def register_tag(self, tag_factory: TagFactory, tag_name: Optional[str] = None):
        if not tag_name:
            tag_class_name = tag_factory.__name__
            if tag_class_name.endswith("Tag"):
                tag_name = tag_class_name[: -len("Tag")]
            else:
                raise ValueError(
                    f"Could not determine tag name from tag class: {tag_class_name}"
                )
        if tag_name in self.tag_registry:
            raise ValueError(f"Factory for tag '{tag_name}' already registered")
        self.tag_registry[tag_name] = tag_factory

    def find_tag(self, tag_name: str) -> Optional[TagFactory]:
        return self.tag_registry.get(tag_name, None)

    def bind(self, pattern: Pattern) -> Pattern:
        return self.rewrite_pattern(pattern)

    def rewrite_pattern(self, pattern: Pattern) -> Pattern:
        new_elements: List[PatternElement] = []
        for element in pattern.sub_elements:
            if isinstance(element, TagPlaceholder):
                new_elements.append(self.rewrite_tag_placeholder(element))
            else:
                new_elements.append(element)
        return Pattern(new_elements)

    def rewrite_tag_placeholder(self, tag_placeholder: TagPlaceholder) -> Tag:
        tag_factory: Optional[TagFactory] = self.find_tag(tag_placeholder.tag_name)
        if not tag_factory:
            raise UnknownTagError(tag_placeholder.tag_name)

        assert "context_present" not in tag_placeholder.kwargs

        if tag_placeholder.context:
            context_pattern = self.rewrite_pattern(tag_placeholder.context)
            return tag_factory(
                *tag_placeholder.args, **tag_placeholder.kwargs, context=context_pattern
            )
        else:
            return tag_factory(
                *tag_placeholder.args, **tag_placeholder.kwargs, context=None
            )
