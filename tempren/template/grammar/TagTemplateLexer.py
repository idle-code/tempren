# Generated from TagTemplateLexer.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\16")
        buf.write("X\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\3\2\3\2\3\2\3\2\3\3\3\3")
        buf.write("\3\3\3\3\3\4\3\4\3\5\3\5\3\6\6\6\60\n\6\r\6\16\6\61\3")
        buf.write("\7\3\7\3\b\3\b\3\b\3\b\3\t\3\t\3\n\3\n\3\n\3\n\3\13\3")
        buf.write("\13\3\f\3\f\3\r\6\rE\n\r\r\r\16\rF\3\16\3\16\5\16K\n\16")
        buf.write("\3\16\3\16\3\16\7\16P\n\16\f\16\16\16S\13\16\3\17\3\17")
        buf.write("\3\20\3\20\2\2\21\4\3\6\4\b\5\n\6\f\7\16\b\20\t\22\n\24")
        buf.write("\13\26\f\30\r\32\16\34\2\36\2 \2\4\2\3\7\4\2\13\f\17\17")
        buf.write("\7\2\13\f\17\17\'\'}}\177\177\5\2\13\f\17\17\"\"\4\2C")
        buf.write("\\c|\3\2\62;\2Y\2\4\3\2\2\2\2\6\3\2\2\2\2\b\3\2\2\2\2")
        buf.write("\n\3\2\2\2\2\f\3\2\2\2\2\16\3\2\2\2\3\20\3\2\2\2\3\22")
        buf.write("\3\2\2\2\3\24\3\2\2\2\3\26\3\2\2\2\3\30\3\2\2\2\3\32\3")
        buf.write("\2\2\2\4\"\3\2\2\2\6&\3\2\2\2\b*\3\2\2\2\n,\3\2\2\2\f")
        buf.write("/\3\2\2\2\16\63\3\2\2\2\20\65\3\2\2\2\229\3\2\2\2\24;")
        buf.write("\3\2\2\2\26?\3\2\2\2\30A\3\2\2\2\32D\3\2\2\2\34J\3\2\2")
        buf.write("\2\36T\3\2\2\2 V\3\2\2\2\"#\t\2\2\2#$\3\2\2\2$%\b\2\2")
        buf.write("\2%\5\3\2\2\2&\'\7\'\2\2\'(\3\2\2\2()\b\3\3\2)\7\3\2\2")
        buf.write("\2*+\7}\2\2+\t\3\2\2\2,-\7\177\2\2-\13\3\2\2\2.\60\n\3")
        buf.write("\2\2/.\3\2\2\2\60\61\3\2\2\2\61/\3\2\2\2\61\62\3\2\2\2")
        buf.write("\62\r\3\2\2\2\63\64\13\2\2\2\64\17\3\2\2\2\65\66\t\4\2")
        buf.write("\2\66\67\3\2\2\2\678\b\b\2\28\21\3\2\2\29:\7*\2\2:\23")
        buf.write("\3\2\2\2;<\7+\2\2<=\3\2\2\2=>\b\n\4\2>\25\3\2\2\2?@\7")
        buf.write(".\2\2@\27\3\2\2\2AB\5\34\16\2B\31\3\2\2\2CE\5 \20\2DC")
        buf.write("\3\2\2\2EF\3\2\2\2FD\3\2\2\2FG\3\2\2\2G\33\3\2\2\2HK\5")
        buf.write("\36\17\2IK\7a\2\2JH\3\2\2\2JI\3\2\2\2KQ\3\2\2\2LP\5\36")
        buf.write("\17\2MP\5 \20\2NP\7a\2\2OL\3\2\2\2OM\3\2\2\2ON\3\2\2\2")
        buf.write("PS\3\2\2\2QO\3\2\2\2QR\3\2\2\2R\35\3\2\2\2SQ\3\2\2\2T")
        buf.write("U\t\5\2\2U\37\3\2\2\2VW\t\6\2\2W!\3\2\2\2\t\2\3\61FJO")
        buf.write("Q\5\b\2\2\7\3\2\6\2\2")
        return buf.getvalue()


class TagTemplateLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    TAG_MODE = 1

    GLOBAL_WHITESPACE = 1
    TAG_START = 2
    CONTEXT_START = 3
    CONTEXT_END = 4
    TEXT = 5
    ANY = 6
    TAG_WHITESPACE = 7
    ARG_START = 8
    ARG_END = 9
    ARG_SEPARATOR = 10
    TAG_ID = 11
    NUMERIC_ARGUMENT = 12

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "TAG_MODE" ]

    literalNames = [ "<INVALID>",
            "'%'", "'{'", "'}'", "'('", "')'", "','" ]

    symbolicNames = [ "<INVALID>",
            "GLOBAL_WHITESPACE", "TAG_START", "CONTEXT_START", "CONTEXT_END", 
            "TEXT", "ANY", "TAG_WHITESPACE", "ARG_START", "ARG_END", "ARG_SEPARATOR", 
            "TAG_ID", "NUMERIC_ARGUMENT" ]

    ruleNames = [ "GLOBAL_WHITESPACE", "TAG_START", "CONTEXT_START", "CONTEXT_END", 
                  "TEXT", "ANY", "TAG_WHITESPACE", "ARG_START", "ARG_END", 
                  "ARG_SEPARATOR", "TAG_ID", "NUMERIC_ARGUMENT", "ID", "LETTER", 
                  "NUMBER_CHAR" ]

    grammarFileName = "TagTemplateLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


