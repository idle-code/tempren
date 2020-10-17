# Generated from TagExpression.g4 by ANTLR 4.8
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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\t")
        buf.write("\24\4\2\t\2\4\3\t\3\3\2\3\2\7\2\t\n\2\f\2\16\2\f\13\2")
        buf.write("\3\2\3\2\3\3\3\3\3\3\3\3\3\3\2\2\4\2\4\2\2\2\23\2\n\3")
        buf.write("\2\2\2\4\17\3\2\2\2\6\t\7\5\2\2\7\t\5\4\3\2\b\6\3\2\2")
        buf.write("\2\b\7\3\2\2\2\t\f\3\2\2\2\n\b\3\2\2\2\n\13\3\2\2\2\13")
        buf.write("\r\3\2\2\2\f\n\3\2\2\2\r\16\7\2\2\3\16\3\3\2\2\2\17\20")
        buf.write("\7\3\2\2\20\21\7\6\2\2\21\22\7\4\2\2\22\5\3\2\2\2\4\b")
        buf.write("\n")
        return buf.getvalue()


class TagExpressionParser ( Parser ):

    grammarFileName = "TagExpression.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'%'", "'()'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "Text", "TagName", 
                      "TagNameStartCharacter", "TagNameCharacter", "WhiteSpace" ]

    RULE_pattern = 0
    RULE_tag = 1

    ruleNames =  [ "pattern", "tag" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    Text=3
    TagName=4
    TagNameStartCharacter=5
    TagNameCharacter=6
    WhiteSpace=7

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
            return self.getToken(TagExpressionParser.EOF, 0)

        def Text(self, i:int=None):
            if i is None:
                return self.getTokens(TagExpressionParser.Text)
            else:
                return self.getToken(TagExpressionParser.Text, i)

        def tag(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TagExpressionParser.TagContext)
            else:
                return self.getTypedRuleContext(TagExpressionParser.TagContext,i)


        def getRuleIndex(self):
            return TagExpressionParser.RULE_pattern

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPattern" ):
                listener.enterPattern(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPattern" ):
                listener.exitPattern(self)




    def pattern(self):

        localctx = TagExpressionParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==TagExpressionParser.T__0 or _la==TagExpressionParser.Text:
                self.state = 6
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [TagExpressionParser.Text]:
                    self.state = 4
                    self.match(TagExpressionParser.Text)
                    pass
                elif token in [TagExpressionParser.T__0]:
                    self.state = 5
                    self.tag()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 10
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 11
            self.match(TagExpressionParser.EOF)
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

        def TagName(self):
            return self.getToken(TagExpressionParser.TagName, 0)

        def getRuleIndex(self):
            return TagExpressionParser.RULE_tag

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTag" ):
                listener.enterTag(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTag" ):
                listener.exitTag(self)




    def tag(self):

        localctx = TagExpressionParser.TagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_tag)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            self.match(TagExpressionParser.T__0)
            self.state = 14
            self.match(TagExpressionParser.TagName)
            self.state = 15
            self.match(TagExpressionParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





