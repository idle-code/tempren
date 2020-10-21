# Generated from TagTemplateLexer.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\17")
        buf.write("e\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\3\2\3\2\3\2\3")
        buf.write("\2\3\3\3\3\3\3\3\3\3\4\3\4\3\5\3\5\3\6\6\6\62\n\6\r\6")
        buf.write("\16\6\63\3\7\3\7\3\b\3\b\3\b\3\b\3\t\3\t\3\n\3\n\3\n\3")
        buf.write("\n\3\13\3\13\3\f\6\fE\n\f\r\f\16\fF\3\r\3\r\3\r\3\r\3")
        buf.write("\r\3\r\3\r\3\r\3\r\5\rR\n\r\3\16\3\16\3\17\3\17\5\17X")
        buf.write("\n\17\3\17\3\17\3\17\7\17]\n\17\f\17\16\17`\13\17\3\20")
        buf.write("\3\20\3\21\3\21\2\2\22\4\3\6\4\b\5\n\6\f\7\16\b\20\t\22")
        buf.write("\n\24\13\26\f\30\r\32\16\34\17\36\2 \2\"\2\4\2\3\7\4\2")
        buf.write("\13\f\17\17\7\2\13\f\17\17\'\'}}\177\177\5\2\13\f\17\17")
        buf.write("\"\"\4\2C\\c|\3\2\62;\2g\2\4\3\2\2\2\2\6\3\2\2\2\2\b\3")
        buf.write("\2\2\2\2\n\3\2\2\2\2\f\3\2\2\2\2\16\3\2\2\2\3\20\3\2\2")
        buf.write("\2\3\22\3\2\2\2\3\24\3\2\2\2\3\26\3\2\2\2\3\30\3\2\2\2")
        buf.write("\3\32\3\2\2\2\3\34\3\2\2\2\4$\3\2\2\2\6(\3\2\2\2\b,\3")
        buf.write("\2\2\2\n.\3\2\2\2\f\61\3\2\2\2\16\65\3\2\2\2\20\67\3\2")
        buf.write("\2\2\22;\3\2\2\2\24=\3\2\2\2\26A\3\2\2\2\30D\3\2\2\2\32")
        buf.write("Q\3\2\2\2\34S\3\2\2\2\36W\3\2\2\2 a\3\2\2\2\"c\3\2\2\2")
        buf.write("$%\t\2\2\2%&\3\2\2\2&\'\b\2\2\2\'\5\3\2\2\2()\7\'\2\2")
        buf.write(")*\3\2\2\2*+\b\3\3\2+\7\3\2\2\2,-\7}\2\2-\t\3\2\2\2./")
        buf.write("\7\177\2\2/\13\3\2\2\2\60\62\n\3\2\2\61\60\3\2\2\2\62")
        buf.write("\63\3\2\2\2\63\61\3\2\2\2\63\64\3\2\2\2\64\r\3\2\2\2\65")
        buf.write("\66\13\2\2\2\66\17\3\2\2\2\678\t\4\2\289\3\2\2\29:\b\b")
        buf.write("\2\2:\21\3\2\2\2;<\7*\2\2<\23\3\2\2\2=>\7+\2\2>?\3\2\2")
        buf.write("\2?@\b\n\4\2@\25\3\2\2\2AB\7.\2\2B\27\3\2\2\2CE\5\"\21")
        buf.write("\2DC\3\2\2\2EF\3\2\2\2FD\3\2\2\2FG\3\2\2\2G\31\3\2\2\2")
        buf.write("HI\7v\2\2IJ\7t\2\2JK\7w\2\2KR\7g\2\2LM\7h\2\2MN\7c\2\2")
        buf.write("NO\7n\2\2OP\7u\2\2PR\7g\2\2QH\3\2\2\2QL\3\2\2\2R\33\3")
        buf.write("\2\2\2ST\5\36\17\2T\35\3\2\2\2UX\5 \20\2VX\7a\2\2WU\3")
        buf.write("\2\2\2WV\3\2\2\2X^\3\2\2\2Y]\5 \20\2Z]\5\"\21\2[]\7a\2")
        buf.write("\2\\Y\3\2\2\2\\Z\3\2\2\2\\[\3\2\2\2]`\3\2\2\2^\\\3\2\2")
        buf.write("\2^_\3\2\2\2_\37\3\2\2\2`^\3\2\2\2ab\t\5\2\2b!\3\2\2\2")
        buf.write("cd\t\6\2\2d#\3\2\2\2\n\2\3\63FQW\\^\5\b\2\2\7\3\2\6\2")
        buf.write("\2")
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
    NUMERIC_ARGUMENT = 11
    BOOLEAN_ARGUMENT = 12
    TAG_ID = 13

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "TAG_MODE" ]

    literalNames = [ "<INVALID>",
            "'%'", "'{'", "'}'", "'('", "')'", "','" ]

    symbolicNames = [ "<INVALID>",
            "GLOBAL_WHITESPACE", "TAG_START", "CONTEXT_START", "CONTEXT_END", 
            "TEXT", "ANY", "TAG_WHITESPACE", "ARG_START", "ARG_END", "ARG_SEPARATOR", 
            "NUMERIC_ARGUMENT", "BOOLEAN_ARGUMENT", "TAG_ID" ]

    ruleNames = [ "GLOBAL_WHITESPACE", "TAG_START", "CONTEXT_START", "CONTEXT_END", 
                  "TEXT", "ANY", "TAG_WHITESPACE", "ARG_START", "ARG_END", 
                  "ARG_SEPARATOR", "NUMERIC_ARGUMENT", "BOOLEAN_ARGUMENT", 
                  "TAG_ID", "ID", "LETTER", "NUMBER_CHAR" ]

    grammarFileName = "TagTemplateLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


