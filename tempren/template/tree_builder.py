import importlib
import inspect
import logging
import pkgutil
from dataclasses import dataclass
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
    TagName,
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
        tag_name: str = ctx.tagId.text  # type: ignore
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
            tag_name=TagName(tag_name, category_name),
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
        error_location = Location(line, column, len(offendingSymbol.text))
        if "extraneous input" in msg or "mismatched input" in msg:
            raise TemplateSyntaxError(
                f"unexpected symbol '{offendingSymbol.text}'"
            ).with_location(error_location)
        else:
            raise TemplateSyntaxError(msg).with_location(error_location)


class TemplateError(Exception):
    """Represents an error in the template itself"""

    message: str
    location: Location
    template: str

    def __init__(self, message: str):
        self.message = message
        self.location = Location(0, 0, 0)

    def with_location(self, location: Location) -> "TemplateError":
        self.location = location
        return self

    def __str__(self) -> str:
        if self.location:
            return f"{self.location}: {self.message}"
        else:
            return self.message


class TemplateSyntaxError(TemplateError):
    pass


class TemplateSemanticError(TemplateError):
    pass


class TagError(TemplateSemanticError):
    tag_name: TagName

    def __init__(self, tag_name: TagName, message: str):
        assert tag_name
        self.tag_name = tag_name
        super().__init__(f"Error in tag '{self.tag_name}': {message}")


class UnknownTagError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"Unknown tag name: {tag_name.name}")

    def with_location(self, whole_name_location: Location) -> "TemplateError":
        if not self.tag_name.category:
            return super().with_location(whole_name_location)
        name_location = Location(
            whole_name_location.line,
            whole_name_location.column + len(self.tag_name.category) + 1,
            len(self.tag_name.name),
        )
        return super().with_location(name_location)


class UnknownCategoryError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"Unknown category name: {tag_name.category}")

    def with_location(self, whole_name_location: Location) -> "TemplateError":
        assert self.tag_name.category
        category_location = Location(
            whole_name_location.line,
            whole_name_location.column,
            len(self.tag_name.category),
        )
        return super().with_location(category_location)


class AmbiguousTagError(TagError):
    category_names: List[str]

    def __init__(self, tag_name: TagName, category_names: List[str]):
        super().__init__(
            tag_name,
            f"This tag name is present in multiple categories: {', '.join(category_names)}",
        )
        self.category_names = category_names


class ContextMissingError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"Context is required for this tag")


class ContextForbiddenError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"This tag cannot be used with context")


class ConfigurationError(TagError):
    def __init__(self, tag_name: TagName, message: str):
        super().__init__(tag_name, f"Configuration not valid: {message}")


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
        category = self.category_map.get(category_name, None)
        if category:
            return category
        category_name = category_name.lower()
        return self.category_map.get(category_name, None)

    def get_tag_factory(self, tag_name: TagName) -> TagFactory:
        if tag_name.category is None:
            return self._get_tag_factory_by_unique_name(tag_name)
        else:
            return self._get_tag_factory_by_name_and_category(tag_name)

    def _get_tag_factory_by_unique_name(self, tag_name: TagName) -> TagFactory:
        # In case there are tags with the same name in multiple categories,
        # category name have to be specified explicitly
        found_tag_factories: Dict[str, TagFactory] = {}
        for category in self.category_map.values():
            tag_factory = category.find_tag_factory(tag_name.name)
            if tag_factory:
                found_tag_factories[category.name] = tag_factory

        if not found_tag_factories:
            raise UnknownTagError(tag_name)
        elif len(found_tag_factories) > 1:
            category_names = sorted(list(found_tag_factories.keys()))
            raise AmbiguousTagError(tag_name, category_names)

        return next(iter(found_tag_factories.values()))

    def _get_tag_factory_by_name_and_category(self, tag_name: TagName) -> TagFactory:
        assert tag_name.category
        tag_category = self.find_category(tag_name.category)
        if tag_category is None:
            raise UnknownCategoryError(tag_name)

        tag_factory = tag_category.find_tag_factory(tag_name.name)
        if tag_factory is None:
            raise UnknownTagError(tag_name)

        return tag_factory

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
        try:
            tag_factory = self.get_tag_factory(tag_placeholder.tag_name)

            self.log.debug(
                "Creating tag '%s' with arguments: %s %s",
                tag_placeholder.tag_name,
                tag_placeholder.args,
                tag_placeholder.kwargs,
            )
            tag = tag_factory(*tag_placeholder.args, **tag_placeholder.kwargs)
        except TemplateError as template_error:
            raise template_error.with_location(tag_placeholder.location)
        except Exception as exc:
            raise ConfigurationError(tag_placeholder.tag_name, str(exc)).with_location(
                tag_placeholder.location
            ) from exc

        if tag.require_context is not None:
            if tag_placeholder.context and not tag.require_context:
                raise ContextForbiddenError(tag_placeholder.tag_name).with_location(
                    tag_placeholder.location
                )
            elif tag_placeholder.context is None and tag.require_context:
                raise ContextMissingError(tag_placeholder.tag_name).with_location(
                    tag_placeholder.location
                )

        context_pattern: Optional[Pattern] = None
        if tag_placeholder.context:
            context_pattern = self._rewrite_pattern(tag_placeholder.context)

        return TagInstance(tag, context=context_pattern)

    def register_category(
        self, category_name: str, description: Optional[str] = None
    ) -> TagCategory:
        # TODO: This method should receive already build (non-empty) TagCategory
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
            if (
                not inspect.isclass(klass)
                or not issubclass(klass, Tag)
                or inspect.isabstract(klass)
                or klass == Tag
            ):
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
            try:
                self.log.debug(f"Trying to load {name} module")
                module = importlib.import_module(name)
                self.register_tags_in_module(module)
            except NotImplementedError as exc:
                self.log.warning(f"Module {name} is currently unsupported: {exc}")
            except Exception as exc:
                self.log.error(exc, f"Could not load module {name}")
