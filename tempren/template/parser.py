from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from lark import (
    Lark,
    Token,
    Transformer,
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
)

from tempren.template.ast import Pattern, RawText, TagPlaceholder
from tempren.template.exceptions import Location, TagName, TemplateSyntaxError
from tempren.template.tree_builder import merge_locations, unescape

grammar_path = Path(__file__).resolve().parent / "grammar.lark"

template_parser = Lark(open(grammar_path), start="pattern")  # , ambiguity='explicit')


class TemplateParser:
    def parse(self, text: str) -> Pattern:
        print(f"Parsed text: {text!r}")
        try:
            tree = template_parser.parse(text)
            print(tree.pretty())
            root_pattern = TreeTransformer().transform(tree)

            print(root_pattern)
            return root_pattern
        except UnexpectedInput as parsing_error:
            context = parsing_error.get_context(text)
            exception = parsing_error.match_examples(
                template_parser.parse,
                {
                    TemplateSyntaxError(
                        message="missing closing argument list bracket"
                    ): ["Some %TAG( text", "%TAG("]
                },
                use_accepts=True,
            )
            location = Location(parsing_error.line, parsing_error.column - 1, length=1)
            raise exception.with_location(location) from parsing_error


def _pairwise(iterable):
    # TODO: For Python 3.10 use pairwise from itertools
    return zip(iterable, iterable[1:])


def _location_from_token(token: Token) -> Location:
    return Location(token.line, token.column, token.end_pos - token.start_pos)


def _without_whitespaces(items: List) -> List:
    return [
        token
        for token in items
        if not (isinstance(token, Token) and token.type == "WS")
    ]


# noinspection PyMethodMayBeStatic
class TreeTransformer(Transformer):
    def pattern(self, items) -> Pattern:
        return Pattern(items)

    def raw_text(self, tokens) -> RawText:
        raw_text = RawText(unescape(tokens[0].value))
        raw_text.location = _location_from_token(tokens[0])
        return raw_text

    def pipe_list(self, items) -> TagPlaceholder:
        pipe_tags: List[TagPlaceholder] = list(
            filter(lambda i: isinstance(i, TagPlaceholder), items)
        )
        for inner, outer in _pairwise(pipe_tags):
            outer.context = Pattern([inner])
        return pipe_tags[-1]

    def tag(self, items) -> TagPlaceholder:
        print("tag item: ", items)
        tag_name = items[0]
        args, kwargs = [], {}
        context = None
        if len(items) > 1:
            if isinstance(items[1], tuple):
                args, kwargs = items[1]
            elif isinstance(items[1], Pattern):
                context = items[1]
        if len(items) > 2 and isinstance(items[2], Pattern):
            context = items[2]
        tag_placeholder = TagPlaceholder(tag_name, context, args, kwargs)
        tag_placeholder.location = tag_name.location
        return tag_placeholder

    def tag_id(self, items) -> TagName:
        if len(items) == 2:
            assert items[0].type == "TAG_CATEGORY"
            assert items[1].type == "TAG_NAME"
            tag_name = TagName(items[1].value, items[0].value)
            category_location = _location_from_token(items[0])
            name_location = _location_from_token(items[1])
            tag_name.location = merge_locations(category_location, name_location)
        else:
            tag_name = TagName(items[0].value)
            tag_name.location = _location_from_token(items[0])
        return tag_name

    def argument_list(self, items) -> Tuple[List, Dict]:
        args = []
        kwargs = {}
        for name, value in _without_whitespaces(items):
            if name is None:
                args.append(value)
            elif value is None:
                kwargs[name] = True
            else:
                kwargs[name] = value
        return args, kwargs

    def argument(self, item) -> Tuple[Optional[str], Any]:
        if isinstance(item[0], tuple):
            return item[0][0], item[0][1]
        else:
            return None, item[0]

    def positional_argument(self, items) -> Tuple[None, Any]:
        return None, items[0]

    def named_argument(self, items) -> Tuple[str, Any]:
        items = _without_whitespaces(items)
        if len(items) == 2:
            return items[0].value, items[1]
        else:
            return items[0].value, True

    def arg_value(self, item) -> Union[int, str, bool]:
        return item[0]

    def numeric_value(self, token) -> int:
        return int(token[0].value)

    def string_value(self, token) -> str:
        return unescape(token[0].value[1:-1])

    def boolean_value(self, token) -> bool:
        return token[0].value.lower() == "true"

    def context(self, items) -> Pattern:
        return items[0]
