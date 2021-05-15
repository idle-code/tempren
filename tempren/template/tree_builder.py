import importlib
import inspect
import logging
import pkgutil
from functools import reduce, wraps
from logging import Logger
from types import ModuleType
from typing import Dict, List, Mapping, Optional, Tuple, Type, Union

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
    TagInstance,
    TagPlaceholder,
)

ArgValue = Union[str, int, bool]


escaped_characters = ("'", "\\", "{", "}", "|")
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
        return self.visitPatternExpression(ctx.patternExpression())

    def visitPatternExpression(
        self, ctx: TagTemplateParser.PatternExpressionContext
    ) -> Pattern:
        pattern = self.visitPattern(ctx.pattern())
        if not ctx.pipeList():
            return pattern

        tag_list = self.visitPipeList(ctx.pipeList())
        context = pattern
        for tag_placeholder in tag_list:
            tag_placeholder.context = context
            context = Pattern([tag_placeholder])
        return context

    def visitPipeList(
        self, ctx: TagTemplateParser.PipeListContext
    ) -> List[TagPlaceholder]:
        tag_list = self.visitChildren(ctx)
        return list(filter(bool, tag_list))

    def visitPattern(self, ctx: TagTemplateParser.PatternContext) -> Pattern:
        pattern_elements = self.visitChildren(ctx)
        return Pattern(pattern_elements)

    def visitContextlessTag(
        self, ctx: TagTemplateParser.ContextlessTagContext
    ) -> TagPlaceholder:
        tag_name = ctx.TAG_ID().getText()
        args, kwargs = self.visitArgumentList(ctx.argumentList())
        tag = TagPlaceholder(tag_name, args=args, kwargs=kwargs, context=None)
        return tag

    def visitTag(self, ctx: TagTemplateParser.TagContext) -> TagPlaceholder:
        tag_name = ctx.TAG_ID().getText()
        args, kwargs = self.visitArgumentList(ctx.argumentList())
        context = self.visitPatternExpression(ctx.patternExpression())
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


class TagError(Exception):
    tag_name: str

    def __init__(self, tag_name: str, message: str):
        assert tag_name
        self.tag_name = tag_name
        super().__init__(f"Error in tag '{self.tag_name}': {message}")


class UnknownTagError(TagError):
    def __init__(self, tag_name: str):
        super().__init__(tag_name, "Tag not recognized")


class ContextMissingError(TagError):
    def __init__(self, tag_name: str):
        super().__init__(tag_name, f"Context is required for this tag")


class ContextForbiddenError(TagError):
    def __init__(self, tag_name: str):
        super().__init__(tag_name, f"This tag cannot be used with context")


class ConfigurationError(TagError):
    def __init__(self, tag_name: str, message: str):
        super().__init__(tag_name, f"Configuration not valid: {message}")


class TagRegistry:
    log: Logger
    _tag_class_suffix = "Tag"
    tag_registry: Dict[str, TagFactory]

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.tag_registry = {}

    def register_tag(self, tag_class: Type[Tag], tag_name: Optional[str] = None):
        if not tag_name:
            tag_class_name = tag_class.__name__
            if tag_class_name.endswith(self._tag_class_suffix):
                tag_name = tag_class_name[: -len(self._tag_class_suffix)]
            else:
                raise ValueError(
                    f"Could not determine tag name from tag class: {tag_class_name}"
                )

        def _simple_tag_factory(*args, **kwargs):
            tag = tag_class()
            tag.configure(*args, **kwargs)
            return tag

        _simple_tag_factory.__doc__ = tag_class.__doc__
        self.log.debug(f"Registering class {tag_class} as {tag_name} tag")
        self.register_tag_factory(_simple_tag_factory, tag_name)

    def register_tag_factory(self, tag_factory: TagFactory, tag_name: str):
        if not tag_name:
            raise ValueError(f"Invalid tag name '{tag_name}'")
        if tag_name in self.tag_registry:
            raise ValueError(f"Factory for tag '{tag_name}' already registered")
        self.tag_registry[tag_name] = tag_factory

    def find_tag_factory(self, tag_name: str) -> Optional[TagFactory]:
        return self.tag_registry.get(tag_name, None)

    def bind(self, pattern: Pattern) -> Pattern:
        return self._rewrite_pattern(pattern)

    def _rewrite_pattern(self, pattern: Pattern) -> Pattern:
        new_elements: List[PatternElement] = []
        for element in pattern.sub_elements:
            if isinstance(element, TagPlaceholder):
                new_elements.append(self._rewrite_tag_placeholder(element))
            else:
                new_elements.append(element)
        return Pattern(new_elements)

    def _rewrite_tag_placeholder(self, tag_placeholder: TagPlaceholder) -> TagInstance:
        tag_factory: Optional[TagFactory] = self.find_tag_factory(
            tag_placeholder.tag_name
        )
        if not tag_factory:
            raise UnknownTagError(tag_placeholder.tag_name)

        try:
            tag = tag_factory(*tag_placeholder.args, **tag_placeholder.kwargs)
        except Exception as exc:
            raise ConfigurationError(tag_placeholder.tag_name, str(exc)) from exc

        if tag.require_context is not None:
            if tag_placeholder.context and not tag.require_context:
                raise ContextForbiddenError(tag_placeholder.tag_name)
            elif tag_placeholder.context is None and tag.require_context:
                raise ContextMissingError(tag_placeholder.tag_name)

        context_pattern: Optional[Pattern] = None
        if tag_placeholder.context:
            context_pattern = self._rewrite_pattern(tag_placeholder.context)

        return TagInstance(tag, context=context_pattern)

    def register_tags_in_module(self, module: ModuleType):
        self.log.debug(f"Discovering tags in module '{module}'")

        def is_tag_class(klass: type):
            if not inspect.isclass(klass) or not issubclass(klass, Tag) or klass == Tag:
                return False
            return klass.__name__.endswith(self._tag_class_suffix)

        for _, tag_class in inspect.getmembers(module, is_tag_class):
            self.register_tag(tag_class)

    def register_tags_in_package(self, package):
        self.log.debug(f"Discovering tags in package '{package}'")

        for _, name, is_pkg in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            if is_pkg:
                continue
            module = importlib.import_module(name)
            self.register_tags_in_module(module)
