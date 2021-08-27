from dataclasses import dataclass
from enum import Enum, auto
from typing import Generator, Iterable, Iterator, List


@dataclass
class Token:
    class Type(Enum):
        RAW_TEXT = auto()
        TAG_START = auto()
        TAG_NAME = auto()
        TAG_ARGS_START = auto()
        TAG_ARGS_END = auto()

    type: Type
    value: str


class Lexer:
    _tokens: List[Token]
    _current: Token
    # _start: int
    # _position: int
    _next_character: Iterator[str]

    def lex(self, input_text: str) -> Iterable[Token]:
        self._reset(input_text)
        return self._lex_expression()

    def _lex_expression(self) -> Iterable[Token]:
        for c in self._next_character:
            if c == "%":
                self._finish_current_token()
                self._lex_token()
            self._current.value += c
        self._finish_current_token()
        return self._tokens

    def _reset(self, input_text: str):
        self._tokens = []
        self._current = Token(Token.Type.RAW_TEXT, "")
        self._next_character = iter(input_text)

    def _finish_current_token(self):
        self._tokens.append(self._current)
        self._current = Token(Token.Type.RAW_TEXT, "")
