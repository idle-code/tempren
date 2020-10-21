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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\16")
        buf.write("\63\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3")
        buf.write("\2\3\2\3\2\3\3\3\3\7\3\24\n\3\f\3\16\3\27\13\3\3\4\3\4")
        buf.write("\3\4\3\4\3\4\3\4\3\4\3\4\3\4\5\4\"\n\4\3\5\3\5\3\5\7\5")
        buf.write("\'\n\5\f\5\16\5*\13\5\3\5\5\5-\n\5\3\6\3\6\3\7\3\7\3\7")
        buf.write("\2\2\b\2\4\6\b\n\f\2\2\2\61\2\16\3\2\2\2\4\25\3\2\2\2")
        buf.write("\6\30\3\2\2\2\b,\3\2\2\2\n.\3\2\2\2\f\60\3\2\2\2\16\17")
        buf.write("\5\4\3\2\17\20\7\2\2\3\20\3\3\2\2\2\21\24\5\f\7\2\22\24")
        buf.write("\5\6\4\2\23\21\3\2\2\2\23\22\3\2\2\2\24\27\3\2\2\2\25")
        buf.write("\23\3\2\2\2\25\26\3\2\2\2\26\5\3\2\2\2\27\25\3\2\2\2\30")
        buf.write("\31\7\4\2\2\31\32\7\r\2\2\32\33\7\n\2\2\33\34\5\b\5\2")
        buf.write("\34!\7\13\2\2\35\36\7\5\2\2\36\37\5\4\3\2\37 \7\6\2\2")
        buf.write(" \"\3\2\2\2!\35\3\2\2\2!\"\3\2\2\2\"\7\3\2\2\2#(\5\n\6")
        buf.write("\2$%\7\f\2\2%\'\5\n\6\2&$\3\2\2\2\'*\3\2\2\2(&\3\2\2\2")
        buf.write("()\3\2\2\2)-\3\2\2\2*(\3\2\2\2+-\3\2\2\2,#\3\2\2\2,+\3")
        buf.write("\2\2\2-\t\3\2\2\2./\7\16\2\2/\13\3\2\2\2\60\61\7\7\2\2")
        buf.write("\61\r\3\2\2\2\7\23\25!(,")
        return buf.getvalue()


class TagTemplateParser ( Parser ):

    grammarFileName = "TagTemplateParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "'%'", "'{'", "'}'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'('", "')'", "','" ]

    symbolicNames = [ "<INVALID>", "GLOBAL_WHITESPACE", "TAG_START", "CONTEXT_START", 
                      "CONTEXT_END", "TEXT", "ANY", "TAG_WHITESPACE", "ARG_START", 
                      "ARG_END", "ARG_SEPARATOR", "TAG_ID", "NUMERIC_ARGUMENT" ]

    RULE_rootPattern = 0
    RULE_pattern = 1
    RULE_tag = 2
    RULE_argumentList = 3
    RULE_argument = 4
    RULE_rawText = 5

    ruleNames =  [ "rootPattern", "pattern", "tag", "argumentList", "argument", 
                   "rawText" ]

    EOF = Token.EOF
    GLOBAL_WHITESPACE=1
    TAG_START=2
    CONTEXT_START=3
    CONTEXT_END=4
    TEXT=5
    ANY=6
    TAG_WHITESPACE=7
    ARG_START=8
    ARG_END=9
    ARG_SEPARATOR=10
    TAG_ID=11
    NUMERIC_ARGUMENT=12

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class RootPatternContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext,0)


        def EOF(self):
            return self.getToken(TagTemplateParser.EOF, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_rootPattern

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRootPattern" ):
                return visitor.visitRootPattern(self)
            else:
                return visitor.visitChildren(self)




    def rootPattern(self):

        localctx = TagTemplateParser.RootPatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_rootPattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 12
            self.pattern()
            self.state = 13
            self.match(TagTemplateParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PatternContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPattern" ):
                return visitor.visitPattern(self)
            else:
                return visitor.visitChildren(self)




    def pattern(self):

        localctx = TagTemplateParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==TagTemplateParser.TAG_START or _la==TagTemplateParser.TEXT:
                self.state = 17
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [TagTemplateParser.TEXT]:
                    self.state = 15
                    self.rawText()
                    pass
                elif token in [TagTemplateParser.TAG_START]:
                    self.state = 16
                    self.tag()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 21
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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
            self.context = None # PatternContext

        def TAG_START(self):
            return self.getToken(TagTemplateParser.TAG_START, 0)

        def TAG_ID(self):
            return self.getToken(TagTemplateParser.TAG_ID, 0)

        def ARG_START(self):
            return self.getToken(TagTemplateParser.ARG_START, 0)

        def argumentList(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentListContext,0)


        def ARG_END(self):
            return self.getToken(TagTemplateParser.ARG_END, 0)

        def CONTEXT_START(self):
            return self.getToken(TagTemplateParser.CONTEXT_START, 0)

        def CONTEXT_END(self):
            return self.getToken(TagTemplateParser.CONTEXT_END, 0)

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext,0)


        def getRuleIndex(self):
            return TagTemplateParser.RULE_tag

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTag" ):
                return visitor.visitTag(self)
            else:
                return visitor.visitChildren(self)




    def tag(self):

        localctx = TagTemplateParser.TagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_tag)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self.match(TagTemplateParser.TAG_START)
            self.state = 23
            self.match(TagTemplateParser.TAG_ID)
            self.state = 24
            self.match(TagTemplateParser.ARG_START)
            self.state = 25
            self.argumentList()
            self.state = 26
            self.match(TagTemplateParser.ARG_END)
            self.state = 31
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==TagTemplateParser.CONTEXT_START:
                self.state = 27
                self.match(TagTemplateParser.CONTEXT_START)
                self.state = 28
                localctx.context = self.pattern()
                self.state = 29
                self.match(TagTemplateParser.CONTEXT_END)


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

        def argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.ArgumentContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.ArgumentContext,i)


        def ARG_SEPARATOR(self, i:int=None):
            if i is None:
                return self.getTokens(TagTemplateParser.ARG_SEPARATOR)
            else:
                return self.getToken(TagTemplateParser.ARG_SEPARATOR, i)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argumentList

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgumentList" ):
                return visitor.visitArgumentList(self)
            else:
                return visitor.visitChildren(self)




    def argumentList(self):

        localctx = TagTemplateParser.ArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_argumentList)
        self._la = 0 # Token type
        try:
            self.state = 42
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [TagTemplateParser.NUMERIC_ARGUMENT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 33
                self.argument()
                self.state = 38
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==TagTemplateParser.ARG_SEPARATOR:
                    self.state = 34
                    self.match(TagTemplateParser.ARG_SEPARATOR)
                    self.state = 35
                    self.argument()
                    self.state = 40
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [TagTemplateParser.ARG_END]:
                self.enterOuterAlt(localctx, 2)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgumentContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMERIC_ARGUMENT(self):
            return self.getToken(TagTemplateParser.NUMERIC_ARGUMENT, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argument

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgument" ):
                return visitor.visitArgument(self)
            else:
                return visitor.visitChildren(self)




    def argument(self):

        localctx = TagTemplateParser.ArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_argument)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.match(TagTemplateParser.NUMERIC_ARGUMENT)
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRawText" ):
                return visitor.visitRawText(self)
            else:
                return visitor.visitChildren(self)




    def rawText(self):

        localctx = TagTemplateParser.RawTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_rawText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            self.match(TagTemplateParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





