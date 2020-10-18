# Generated from TagTemplateLexer.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\13")
        buf.write("G\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\3\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\4\3\4\3\5\3\5\3\6\6")
        buf.write("\6*\n\6\r\6\16\6+\3\7\3\7\3\b\3\b\3\t\3\t\3\t\3\t\3\n")
        buf.write("\3\n\3\13\3\13\5\13:\n\13\3\13\3\13\3\13\7\13?\n\13\f")
        buf.write("\13\16\13B\13\13\3\f\3\f\3\r\3\r\2\2\16\4\3\6\4\b\5\n")
        buf.write("\6\f\7\16\b\20\t\22\n\24\13\26\2\30\2\32\2\4\2\3\6\4\2")
        buf.write("\13\f\17\17\7\2\13\f\17\17\'\'}}\177\177\4\2C\\c|\3\2")
        buf.write("\62;\2G\2\4\3\2\2\2\2\6\3\2\2\2\2\b\3\2\2\2\2\n\3\2\2")
        buf.write("\2\2\f\3\2\2\2\2\16\3\2\2\2\3\20\3\2\2\2\3\22\3\2\2\2")
        buf.write("\3\24\3\2\2\2\4\34\3\2\2\2\6 \3\2\2\2\b$\3\2\2\2\n&\3")
        buf.write("\2\2\2\f)\3\2\2\2\16-\3\2\2\2\20/\3\2\2\2\22\61\3\2\2")
        buf.write("\2\24\65\3\2\2\2\269\3\2\2\2\30C\3\2\2\2\32E\3\2\2\2\34")
        buf.write("\35\t\2\2\2\35\36\3\2\2\2\36\37\b\2\2\2\37\5\3\2\2\2 ")
        buf.write("!\7\'\2\2!\"\3\2\2\2\"#\b\3\3\2#\7\3\2\2\2$%\7}\2\2%\t")
        buf.write("\3\2\2\2&\'\7\177\2\2\'\13\3\2\2\2(*\n\3\2\2)(\3\2\2\2")
        buf.write("*+\3\2\2\2+)\3\2\2\2+,\3\2\2\2,\r\3\2\2\2-.\13\2\2\2.")
        buf.write("\17\3\2\2\2/\60\7*\2\2\60\21\3\2\2\2\61\62\7+\2\2\62\63")
        buf.write("\3\2\2\2\63\64\b\t\4\2\64\23\3\2\2\2\65\66\5\26\13\2\66")
        buf.write("\25\3\2\2\2\67:\5\30\f\28:\7a\2\29\67\3\2\2\298\3\2\2")
        buf.write("\2:@\3\2\2\2;?\5\30\f\2<?\5\32\r\2=?\7a\2\2>;\3\2\2\2")
        buf.write("><\3\2\2\2>=\3\2\2\2?B\3\2\2\2@>\3\2\2\2@A\3\2\2\2A\27")
        buf.write("\3\2\2\2B@\3\2\2\2CD\t\4\2\2D\31\3\2\2\2EF\t\5\2\2F\33")
        buf.write("\3\2\2\2\b\2\3+9>@\5\b\2\2\7\3\2\6\2\2")
        return buf.getvalue()


class TagTemplateLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    TAG_MODE = 1

    INVALID_WHITESPACE = 1
    TAG_START = 2
    CONTEXT_START = 3
    CONTEXT_END = 4
    TEXT = 5
    ANY = 6
    ARG_START = 7
    ARG_END = 8
    TAG_ID = 9

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "TAG_MODE" ]

    literalNames = [ "<INVALID>",
            "'%'", "'{'", "'}'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>",
            "INVALID_WHITESPACE", "TAG_START", "CONTEXT_START", "CONTEXT_END", 
            "TEXT", "ANY", "ARG_START", "ARG_END", "TAG_ID" ]

    ruleNames = [ "INVALID_WHITESPACE", "TAG_START", "CONTEXT_START", "CONTEXT_END", 
                  "TEXT", "ANY", "ARG_START", "ARG_END", "TAG_ID", "ID", 
                  "LETTER", "NUMBER" ]

    grammarFileName = "TagTemplateLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


