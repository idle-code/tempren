# Generated from TagExpression.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\t")
        buf.write(",\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\3\2\3\2\3\3\3\3\3\3\3\4\6\4\30\n\4\r\4\16\4\31")
        buf.write("\3\5\3\5\7\5\36\n\5\f\5\16\5!\13\5\3\6\3\6\3\7\3\7\5\7")
        buf.write("\'\n\7\3\b\3\b\3\b\3\b\2\2\t\3\3\5\4\7\5\t\6\13\7\r\b")
        buf.write("\17\t\3\2\6\6\2\"\"\62;C\\c|\5\2C\\aac|\3\2\62;\4\2\13")
        buf.write("\f\17\17\2.\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3")
        buf.write("\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\3\21\3\2")
        buf.write("\2\2\5\23\3\2\2\2\7\27\3\2\2\2\t\33\3\2\2\2\13\"\3\2\2")
        buf.write("\2\r&\3\2\2\2\17(\3\2\2\2\21\22\7\'\2\2\22\4\3\2\2\2\23")
        buf.write("\24\7*\2\2\24\25\7+\2\2\25\6\3\2\2\2\26\30\t\2\2\2\27")
        buf.write("\26\3\2\2\2\30\31\3\2\2\2\31\27\3\2\2\2\31\32\3\2\2\2")
        buf.write("\32\b\3\2\2\2\33\37\5\13\6\2\34\36\5\r\7\2\35\34\3\2\2")
        buf.write("\2\36!\3\2\2\2\37\35\3\2\2\2\37 \3\2\2\2 \n\3\2\2\2!\37")
        buf.write("\3\2\2\2\"#\t\3\2\2#\f\3\2\2\2$\'\5\13\6\2%\'\t\4\2\2")
        buf.write("&$\3\2\2\2&%\3\2\2\2\'\16\3\2\2\2()\t\5\2\2)*\3\2\2\2")
        buf.write("*+\b\b\2\2+\20\3\2\2\2\6\2\31\37&\3\b\2\2")
        return buf.getvalue()


class TagExpressionLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    Text = 3
    TagName = 4
    TagNameStartCharacter = 5
    TagNameCharacter = 6
    WhiteSpace = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'%'", "'()'" ]

    symbolicNames = [ "<INVALID>",
            "Text", "TagName", "TagNameStartCharacter", "TagNameCharacter", 
            "WhiteSpace" ]

    ruleNames = [ "T__0", "T__1", "Text", "TagName", "TagNameStartCharacter", 
                  "TagNameCharacter", "WhiteSpace" ]

    grammarFileName = "TagExpression.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


