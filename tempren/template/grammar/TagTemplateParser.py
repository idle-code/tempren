# Generated from TagTemplateParser.g4 by ANTLR 4.8
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\b")
        buf.write("\31\4\2\t\2\4\3\t\3\4\4\t\4\3\2\3\2\7\2\13\n\2\f\2\16")
        buf.write("\2\16\13\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3\4\2\2")
        buf.write("\5\2\4\6\2\2\2\27\2\f\3\2\2\2\4\21\3\2\2\2\6\26\3\2\2")
        buf.write("\2\b\13\5\6\4\2\t\13\5\4\3\2\n\b\3\2\2\2\n\t\3\2\2\2\13")
        buf.write("\16\3\2\2\2\f\n\3\2\2\2\f\r\3\2\2\2\r\17\3\2\2\2\16\f")
        buf.write("\3\2\2\2\17\20\7\2\2\3\20\3\3\2\2\2\21\22\7\3\2\2\22\23")
        buf.write("\7\b\2\2\23\24\7\6\2\2\24\25\7\7\2\2\25\5\3\2\2\2\26\27")
        buf.write("\7\4\2\2\27\7\3\2\2\2\4\n\f")
        return buf.getvalue()


class TagTemplateParser ( Parser ):

    grammarFileName = "TagTemplateParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'%'", "<INVALID>", "<INVALID>", "'('", 
                     "')'" ]

    symbolicNames = [ "<INVALID>", "TAG_START", "TEXT", "INVALID_WHITESPACE", 
                      "ARG_START", "ARG_END", "TAG_ID" ]

    RULE_pattern = 0
    RULE_tag = 1
    RULE_rawText = 2

    ruleNames =  [ "pattern", "tag", "rawText" ]

    EOF = Token.EOF
    TAG_START=1
    TEXT=2
    INVALID_WHITESPACE=3
    ARG_START=4
    ARG_END=5
    TAG_ID=6

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class PatternContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(TagTemplateParser.EOF, 0)

        def rawText(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.RawTextContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.RawTextContext,i)


        def tag(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.TagContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.TagContext,i)


        def getRuleIndex(self):
            return TagTemplateParser.RULE_pattern

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPattern" ):
                listener.enterPattern(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPattern" ):
                listener.exitPattern(self)




    def pattern(self):

        localctx = TagTemplateParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==TagTemplateParser.TAG_START or _la==TagTemplateParser.TEXT:
                self.state = 8
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [TagTemplateParser.TEXT]:
                    self.state = 6
                    self.rawText()
                    pass
                elif token in [TagTemplateParser.TAG_START]:
                    self.state = 7
                    self.tag()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 12
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 13
            self.match(TagTemplateParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TagContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TAG_START(self):
            return self.getToken(TagTemplateParser.TAG_START, 0)

        def TAG_ID(self):
            return self.getToken(TagTemplateParser.TAG_ID, 0)

        def ARG_START(self):
            return self.getToken(TagTemplateParser.ARG_START, 0)

        def ARG_END(self):
            return self.getToken(TagTemplateParser.ARG_END, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_tag

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTag" ):
                listener.enterTag(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTag" ):
                listener.exitTag(self)




    def tag(self):

        localctx = TagTemplateParser.TagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_tag)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self.match(TagTemplateParser.TAG_START)
            self.state = 16
            self.match(TagTemplateParser.TAG_ID)
            self.state = 17
            self.match(TagTemplateParser.ARG_START)
            self.state = 18
            self.match(TagTemplateParser.ARG_END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RawTextContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self):
            return self.getToken(TagTemplateParser.TEXT, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_rawText

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRawText" ):
                listener.enterRawText(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRawText" ):
                listener.exitRawText(self)




    def rawText(self):

        localctx = TagTemplateParser.RawTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_rawText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.match(TagTemplateParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





