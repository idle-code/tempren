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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\n")
        buf.write("%\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\3\2\3\2\7\2")
        buf.write("\17\n\2\f\2\16\2\22\13\2\3\2\3\2\3\3\3\3\3\3\3\3\5\3\32")
        buf.write("\n\3\3\4\3\4\3\4\3\5\3\5\3\5\3\5\3\6\3\6\3\6\2\2\7\2\4")
        buf.write("\6\b\n\2\2\2\"\2\20\3\2\2\2\4\25\3\2\2\2\6\33\3\2\2\2")
        buf.write("\b\36\3\2\2\2\n\"\3\2\2\2\f\17\5\n\6\2\r\17\5\4\3\2\16")
        buf.write("\f\3\2\2\2\16\r\3\2\2\2\17\22\3\2\2\2\20\16\3\2\2\2\20")
        buf.write("\21\3\2\2\2\21\23\3\2\2\2\22\20\3\2\2\2\23\24\7\2\2\3")
        buf.write("\24\3\3\2\2\2\25\26\7\4\2\2\26\27\7\n\2\2\27\31\5\6\4")
        buf.write("\2\30\32\5\b\5\2\31\30\3\2\2\2\31\32\3\2\2\2\32\5\3\2")
        buf.write("\2\2\33\34\7\b\2\2\34\35\7\t\2\2\35\7\3\2\2\2\36\37\7")
        buf.write("\6\2\2\37 \5\2\2\2 !\7\7\2\2!\t\3\2\2\2\"#\7\5\2\2#\13")
        buf.write("\3\2\2\2\5\16\20\31")
        return buf.getvalue()


class TagTemplateParser ( Parser ):

    grammarFileName = "TagTemplateParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "'%'", "<INVALID>", "'{'", 
                     "'}'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "INVALID_WHITESPACE", "TAG_START", "TEXT", 
                      "CONTEXT_START", "CONTEXT_END", "ARG_START", "ARG_END", 
                      "TAG_ID" ]

    RULE_pattern = 0
    RULE_tag = 1
    RULE_argumentList = 2
    RULE_tagContext = 3
    RULE_rawText = 4

    ruleNames =  [ "pattern", "tag", "argumentList", "tagContext", "rawText" ]

    EOF = Token.EOF
    INVALID_WHITESPACE=1
    TAG_START=2
    TEXT=3
    CONTEXT_START=4
    CONTEXT_END=5
    ARG_START=6
    ARG_END=7
    TAG_ID=8

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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPattern" ):
                return visitor.visitPattern(self)
            else:
                return visitor.visitChildren(self)




    def pattern(self):

        localctx = TagTemplateParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 14
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==TagTemplateParser.TAG_START or _la==TagTemplateParser.TEXT:
                self.state = 12
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [TagTemplateParser.TEXT]:
                    self.state = 10
                    self.rawText()
                    pass
                elif token in [TagTemplateParser.TAG_START]:
                    self.state = 11
                    self.tag()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 16
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 17
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

        def argumentList(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentListContext,0)


        def tagContext(self):
            return self.getTypedRuleContext(TagTemplateParser.TagContextContext,0)


        def getRuleIndex(self):
            return TagTemplateParser.RULE_tag

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTag" ):
                listener.enterTag(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTag" ):
                listener.exitTag(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTag" ):
                return visitor.visitTag(self)
            else:
                return visitor.visitChildren(self)




    def tag(self):

        localctx = TagTemplateParser.TagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_tag)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self.match(TagTemplateParser.TAG_START)
            self.state = 20
            self.match(TagTemplateParser.TAG_ID)
            self.state = 21
            self.argumentList()
            self.state = 23
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==TagTemplateParser.CONTEXT_START:
                self.state = 22
                self.tagContext()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgumentListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ARG_START(self):
            return self.getToken(TagTemplateParser.ARG_START, 0)

        def ARG_END(self):
            return self.getToken(TagTemplateParser.ARG_END, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArgumentList" ):
                listener.enterArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArgumentList" ):
                listener.exitArgumentList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgumentList" ):
                return visitor.visitArgumentList(self)
            else:
                return visitor.visitChildren(self)




    def argumentList(self):

        localctx = TagTemplateParser.ArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_argumentList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25
            self.match(TagTemplateParser.ARG_START)
            self.state = 26
            self.match(TagTemplateParser.ARG_END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TagContextContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONTEXT_START(self):
            return self.getToken(TagTemplateParser.CONTEXT_START, 0)

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext,0)


        def CONTEXT_END(self):
            return self.getToken(TagTemplateParser.CONTEXT_END, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_tagContext

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTagContext" ):
                listener.enterTagContext(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTagContext" ):
                listener.exitTagContext(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTagContext" ):
                return visitor.visitTagContext(self)
            else:
                return visitor.visitChildren(self)




    def tagContext(self):

        localctx = TagTemplateParser.TagContextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_tagContext)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.match(TagTemplateParser.CONTEXT_START)
            self.state = 29
            self.pattern()
            self.state = 30
            self.match(TagTemplateParser.CONTEXT_END)
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRawText" ):
                return visitor.visitRawText(self)
            else:
                return visitor.visitChildren(self)




    def rawText(self):

        localctx = TagTemplateParser.RawTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_rawText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 32
            self.match(TagTemplateParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





