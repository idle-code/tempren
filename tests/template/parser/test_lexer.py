from typing import Iterable, Tuple

from tempren.template.parser.lexer import Lexer, Token


class TestLexer:
    def lex(self, input_text: str) -> Iterable[Token]:
        lexer = Lexer()
        return lexer.lex(input_text)

    def compare_token_types(
        self, actual: Iterable[Token], expected_types: Iterable[Token.Type]
    ):
        actual_token_types = list(map(lambda t: t.type, actual))
        assert actual_token_types == expected_types

    def test_raw_text_is_recognized(self):
        tokens = self.lex("Raw text")

        self.compare_token_types(tokens, [Token.Type.RAW_TEXT])

    def test_tag_is_recognized(self):
        tokens = self.lex("%TAG()")

        self.compare_token_types(
            tokens,
            [
                Token.Type.TAG_START,
                Token.Type.TAG_NAME,
                Token.Type.TAG_ARGS_START,
                Token.Type.TAG_ARGS_END,
            ],
        )
