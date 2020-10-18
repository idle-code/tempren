# Generated from TagTemplateLexer.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\b")
        buf.write("?\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\3\2\3\2\3\2\3\2")
        buf.write("\3\3\6\3\36\n\3\r\3\16\3\37\3\4\3\4\3\5\3\5\3\5\3\5\3")
        buf.write("\6\3\6\3\7\3\7\3\7\3\7\3\b\3\b\3\t\3\t\5\t\62\n\t\3\t")
        buf.write("\3\t\3\t\7\t\67\n\t\f\t\16\t:\13\t\3\n\3\n\3\13\3\13\2")
        buf.write("\2\f\4\3\6\4\b\2\n\5\f\6\16\7\20\b\22\2\24\2\26\2\4\2")
        buf.write("\3\6\3\2\'\'\4\2\13\f\17\17\4\2C\\c|\3\2\62;\2>\2\4\3")
        buf.write("\2\2\2\2\6\3\2\2\2\2\n\3\2\2\2\3\f\3\2\2\2\3\16\3\2\2")
        buf.write("\2\3\20\3\2\2\2\4\30\3\2\2\2\6\35\3\2\2\2\b!\3\2\2\2\n")
        buf.write("#\3\2\2\2\f\'\3\2\2\2\16)\3\2\2\2\20-\3\2\2\2\22\61\3")
        buf.write("\2\2\2\24;\3\2\2\2\26=\3\2\2\2\30\31\7\'\2\2\31\32\3\2")
        buf.write("\2\2\32\33\b\2\2\2\33\5\3\2\2\2\34\36\n\2\2\2\35\34\3")
        buf.write("\2\2\2\36\37\3\2\2\2\37\35\3\2\2\2\37 \3\2\2\2 \7\3\2")
        buf.write("\2\2!\"\t\3\2\2\"\t\3\2\2\2#$\5\b\4\2$%\3\2\2\2%&\b\5")
        buf.write("\3\2&\13\3\2\2\2\'(\7*\2\2(\r\3\2\2\2)*\7+\2\2*+\3\2\2")
        buf.write("\2+,\b\7\4\2,\17\3\2\2\2-.\5\22\t\2.\21\3\2\2\2/\62\5")
        buf.write("\24\n\2\60\62\7a\2\2\61/\3\2\2\2\61\60\3\2\2\2\628\3\2")
        buf.write("\2\2\63\67\5\24\n\2\64\67\5\26\13\2\65\67\7a\2\2\66\63")
        buf.write("\3\2\2\2\66\64\3\2\2\2\66\65\3\2\2\2\67:\3\2\2\28\66\3")
        buf.write("\2\2\289\3\2\2\29\23\3\2\2\2:8\3\2\2\2;<\t\4\2\2<\25\3")
        buf.write("\2\2\2=>\t\5\2\2>\27\3\2\2\2\b\2\3\37\61\668\5\7\3\2\b")
        buf.write("\2\2\6\2\2")
        return buf.getvalue()


class TagTemplateLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    TAG_MODE = 1

    TAG_START = 1
    TEXT = 2
    INVALID_WHITESPACE = 3
    ARG_START = 4
    ARG_END = 5
    TAG_ID = 6

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "TAG_MODE" ]

    literalNames = [ "<INVALID>",
            "'%'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>",
            "TAG_START", "TEXT", "INVALID_WHITESPACE", "ARG_START", "ARG_END", 
            "TAG_ID" ]

    ruleNames = [ "TAG_START", "TEXT", "INVALID_WHITESPACE_CHAR", "INVALID_WHITESPACE", 
                  "ARG_START", "ARG_END", "TAG_ID", "ID", "LETTER", "NUMBER" ]

    grammarFileName = "TagTemplateLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


