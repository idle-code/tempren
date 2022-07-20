import importlib
import inspect
import logging
import pkgutil
from functools import reduce
from logging import Logger
from types import ModuleType
from typing import Dict, List, Mapping, Optional, Tuple, Type, Union

from antlr4 import CommonTokenStream, InputStream  # type: ignore
from antlr4.error.ErrorListener import ErrorListener  # type: ignore

from .grammar.TagTemplateLexer import TagTemplateLexer
from .grammar.TagTemplateParser import TagTemplateParser
from .grammar.TagTemplateParserVisitor import TagTemplateParserVisitor
from .tree_elements import (
    Location,
    Pattern,
    PatternElement,
    RawText,
    Tag,
    TagFactory,
    TagFactoryFromClass,
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


class _TreeVisitor(TagTemplateParserVisitor):
    def defaultResult(self) -> List[PatternElement]:
        return list()

    def visitTerminal(self, node):
        if node.getSymbol().type not in ARGUMENT_VALUE_TYPES:
            return IGNORED_TERMINAL
        return self.defaultResult()

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
            raise TagTemplateSyntaxError(
                location_from_symbol(non_tag_symbol),
                message=f"non-tag in the pipe list",
            )
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
        if ctx.errorMissingTagId:
            raise TagTemplateSyntaxError(
                location_from_symbol(ctx.errorMissingTagId),
                message=f"missing tag name",
            )
        tag_name = ctx.TAG_ID().getText()
        if ctx.errorNoArgumentList:
            raise TagTemplateSyntaxError(
                location_from_symbol(ctx.errorNoArgumentList),
                message=f"missing argument list for tag '{tag_name}'",
            )
        if ctx.errorUnclosedContext:
            raise TagTemplateSyntaxError(
                location_from_symbol(ctx.errorUnclosedContext),
                message=f"missing closing context bracket for tag '{tag_name}'",
            )
        args, kwargs = self.visitArgumentList(ctx.argumentList())
        context = None
        context_pattern = ctx.pattern()
        if context_pattern is not None:
            context = self.visitPattern(ctx.pattern())

        tag = TagPlaceholder(
            tag_name=tag_name,
            args=args,
            kwargs=kwargs,
            context=context,
        )
        symbol = ctx.TAG_ID().getSymbol()
        tag.location = location_from_symbol(symbol)
        return tag

    def visitArgumentList(
        self, ctx: TagTemplateParser.ArgumentListContext
    ) -> Tuple[List[ArgValue], Mapping[str, ArgValue]]:
        if ctx.errorUnclosedArgumentList:
            raise TagTemplateSyntaxError(
                location_from_symbol(ctx.errorUnclosedArgumentList),
                message="missing closing argument list bracket",
            )
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


class TagTreeBuilder:
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
        from pprint import pprint

        # pprint([">>>>>///", recognizer, offendingSymbol, line, column, msg, e])
        error_location = Location(line, column, len(offendingSymbol.text))
        if "extraneous input" in msg or "mismatched input" in msg:
            raise TagTemplateSyntaxError(
                error_location,
                f"unexpected symbol '{offendingSymbol.text}'",
            )
        raise TagTemplateSyntaxError(error_location, msg)

    def reportAmbiguity(
        self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs
    ):
        # print("reportAmbiguity")
        super().reportAmbiguity(
            recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs
        )

    def reportAttemptingFullContext(
        self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs
    ):
        # print("reportAttemptingFullContext")
        super().reportAttemptingFullContext(
            recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs
        )

    def reportContextSensitivity(
        self, recognizer, dfa, startIndex, stopIndex, prediction, configs
    ):
        # print("reportContextSensitivity")
        super().reportContextSensitivity(
            recognizer, dfa, startIndex, stopIndex, prediction, configs
        )


class TemplateError(Exception):
    """Represents an error in the template itself"""

    location: Location
    message: str
    template: str

    def __init__(self, location: Location, message: str):
        super().__init__(f"{location}: {message}")
        self.location = location
        self.message = message


class TagTemplateSyntaxError(TemplateError):
    pass


class TagTemplateSemanticError(TemplateError):
    pass


class TagError(TagTemplateSemanticError):
    tag_name: str

    def __init__(self, location: Location, tag_name: str, message: str):
        assert tag_name
        self.tag_name = tag_name
        super().__init__(location, f"Error in tag '{self.tag_name}': {message}")


class UnknownTagError(TagError):
    def __init__(self, location: Location, tag_name: str):
        super().__init__(location, tag_name, "Tag not recognized")


class ContextMissingError(TagError):
    def __init__(self, location: Location, tag_name: str):
        super().__init__(location, tag_name, f"Context is required for this tag")


class ContextForbiddenError(TagError):
    def __init__(self, location: Location, tag_name: str):
        super().__init__(location, tag_name, f"This tag cannot be used with context")


class ConfigurationError(TagError):
    def __init__(self, location: Location, tag_name: str, message: str):
        super().__init__(location, tag_name, f"Configuration not valid: {message}")


class TagCategory:
    log: Logger

    name: str
    description: Optional[str] = None
    tag_map: Dict[str, TagFactory]

    def __init__(self, name: str, description: Optional[str] = None):
        self.log = logging.getLogger(self.__class__.__name__)
        self.tag_map = {}
        self.name = name
        self.description = description

    def register_tag(self, tag_class: Type[Tag], tag_name: Optional[str] = None):
        _simple_tag_factory = TagFactoryFromClass(tag_class, tag_name)
        self.log.debug(
            f"Registering class {tag_class} as {_simple_tag_factory.tag_name} tag"
        )
        self.register_tag_factory(_simple_tag_factory, tag_name)

    def register_tag_factory(
        self, tag_factory: TagFactory, tag_name: Optional[str] = None
    ):
        if tag_name is None:
            tag_name = tag_factory.tag_name
        if not tag_name:
            raise ValueError(f"Invalid tag name '{repr(tag_name)}'")
        if tag_name in self.tag_map:
            raise ValueError(f"Factory for tag '{tag_name}' already registered")
        self.tag_map[tag_name] = tag_factory

    def find_tag_factory(self, tag_name: str) -> Optional[TagFactory]:
        return self.tag_map.get(tag_name, None)


class TagRegistry:
    log: Logger
    _tag_class_suffix = "Tag"
    category_map: Dict[str, TagCategory]

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.category_map = {}

    @property
    def categories(self) -> List[str]:
        return sorted(self.category_map.keys())

    def find_category(self, category_name: str) -> Optional[TagCategory]:
        return self.category_map.get(category_name, None)

    def find_tag_factory(self, tag_name: str) -> Optional[TagFactory]:
        for category in self.category_map.values():
            tag_factory = category.find_tag_factory(tag_name)
            if tag_factory:
                return tag_factory
        return None

    def bind(self, pattern: Pattern) -> Pattern:
        return self._rewrite_pattern(pattern)

    def _rewrite_pattern(self, pattern: Pattern) -> Pattern:
        new_elements: List[PatternElement] = []
        for element in pattern.sub_elements:
            if isinstance(element, TagPlaceholder):
                new_elements.append(self._rewrite_tag_placeholder(element))
            else:
                new_elements.append(element)
        bound_pattern = Pattern(new_elements)
        bound_pattern.source_representation = pattern.source_representation
        return bound_pattern

    def _rewrite_tag_placeholder(self, tag_placeholder: TagPlaceholder) -> TagInstance:
        tag_factory: Optional[TagFactory] = self.find_tag_factory(
            tag_placeholder.tag_name
        )
        if not tag_factory:
            raise UnknownTagError(tag_placeholder.location, tag_placeholder.tag_name)

        try:
            self.log.debug(
                "Creating tag '%s' with arguments: %s %s",
                tag_placeholder.tag_name,
                tag_placeholder.args,
                tag_placeholder.kwargs,
            )
            tag = tag_factory(*tag_placeholder.args, **tag_placeholder.kwargs)
        except Exception as exc:
            raise ConfigurationError(
                tag_placeholder.location, tag_placeholder.tag_name, str(exc)
            ) from exc

        if tag.require_context is not None:
            if tag_placeholder.context and not tag.require_context:
                raise ContextForbiddenError(
                    tag_placeholder.location, tag_placeholder.tag_name
                )
            elif tag_placeholder.context is None and tag.require_context:
                raise ContextMissingError(
                    tag_placeholder.location, tag_placeholder.tag_name
                )

        context_pattern: Optional[Pattern] = None
        if tag_placeholder.context:
            context_pattern = self._rewrite_pattern(tag_placeholder.context)

        return TagInstance(tag, context=context_pattern)

    def register_category(
        self, category_name: str, description: Optional[str] = None
    ) -> TagCategory:
        if self.find_category(category_name) is not None:
            raise ValueError(f"Category '{category_name}' already registered")
        new_category = TagCategory(category_name)
        self.category_map[category_name] = new_category
        return new_category

    def register_tags_in_module(self, module: ModuleType):
        self.log.debug(f"Discovering tags in module '{module}'")

        if module.__package__:
            category_name = module.__name__[len(module.__package__) + 1 :]
        else:
            category_name = module.__name__

        def is_tag_class(klass: type):
            if not inspect.isclass(klass) or not issubclass(klass, Tag) or klass == Tag:
                return False
            return klass.__name__.endswith(self._tag_class_suffix)

        # TODO: do not register empty modules
        module_category = self.register_category(category_name)
        for _, tag_class in inspect.getmembers(module, is_tag_class):
            module_category.register_tag(tag_class)

    def register_tags_in_package(self, package):
        self.log.debug(f"Discovering tags in package '{package}'")

        for _, name, is_pkg in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            if is_pkg:
                continue
            module = importlib.import_module(name)
            self.register_tags_in_module(module)
