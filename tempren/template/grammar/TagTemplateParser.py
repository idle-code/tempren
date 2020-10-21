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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\22")
        buf.write(">\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\3\2\3\2\3\2\3\3\3\3\7\3\26\n\3\f\3\16\3\31\13\3\3")
        buf.write("\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\5\4$\n\4\3\5\3\5\3")
        buf.write("\5\7\5)\n\5\f\5\16\5,\13\5\3\5\5\5/\n\5\3\6\3\6\3\6\5")
        buf.write("\6\64\n\6\3\7\3\7\5\78\n\7\3\7\3\7\3\b\3\b\3\b\2\2\t\2")
        buf.write("\4\6\b\n\f\16\2\2\2>\2\20\3\2\2\2\4\27\3\2\2\2\6\32\3")
        buf.write("\2\2\2\b.\3\2\2\2\n\63\3\2\2\2\f\65\3\2\2\2\16;\3\2\2")
        buf.write("\2\20\21\5\4\3\2\21\22\7\2\2\3\22\3\3\2\2\2\23\26\5\16")
        buf.write("\b\2\24\26\5\6\4\2\25\23\3\2\2\2\25\24\3\2\2\2\26\31\3")
        buf.write("\2\2\2\27\25\3\2\2\2\27\30\3\2\2\2\30\5\3\2\2\2\31\27")
        buf.write("\3\2\2\2\32\33\7\4\2\2\33\34\7\20\2\2\34\35\7\n\2\2\35")
        buf.write("\36\5\b\5\2\36#\7\13\2\2\37 \7\5\2\2 !\5\4\3\2!\"\7\6")
        buf.write("\2\2\"$\3\2\2\2#\37\3\2\2\2#$\3\2\2\2$\7\3\2\2\2%*\5\n")
        buf.write("\6\2&\'\7\f\2\2\')\5\n\6\2(&\3\2\2\2),\3\2\2\2*(\3\2\2")
        buf.write("\2*+\3\2\2\2+/\3\2\2\2,*\3\2\2\2-/\3\2\2\2.%\3\2\2\2.")
        buf.write("-\3\2\2\2/\t\3\2\2\2\60\64\7\16\2\2\61\64\7\r\2\2\62\64")
        buf.write("\5\f\7\2\63\60\3\2\2\2\63\61\3\2\2\2\63\62\3\2\2\2\64")
        buf.write("\13\3\2\2\2\65\67\7\17\2\2\668\7\21\2\2\67\66\3\2\2\2")
        buf.write("\678\3\2\2\289\3\2\2\29:\7\22\2\2:\r\3\2\2\2;<\7\7\2\2")
        buf.write("<\17\3\2\2\2\t\25\27#*.\63\67")
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
                      "ARG_END", "ARG_SEPARATOR", "NUMERIC_VALUE", "BOOLEAN_VALUE", 
                      "STRING_START", "TAG_ID", "STRING_VALUE", "STRING_END" ]

    RULE_rootPattern = 0
    RULE_pattern = 1
    RULE_tag = 2
    RULE_argumentList = 3
    RULE_argument = 4
    RULE_stringLiteral = 5
    RULE_rawText = 6

    ruleNames =  [ "rootPattern", "pattern", "tag", "argumentList", "argument", 
                   "stringLiteral", "rawText" ]

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
    NUMERIC_VALUE=11
    BOOLEAN_VALUE=12
    STRING_START=13
    TAG_ID=14
    STRING_VALUE=15
    STRING_END=16

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
            self.state = 14
            self.pattern()
            self.state = 15
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
            self.state = 21
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==TagTemplateParser.TAG_START or _la==TagTemplateParser.TEXT:
                self.state = 19
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [TagTemplateParser.TEXT]:
                    self.state = 17
                    self.rawText()
                    pass
                elif token in [TagTemplateParser.TAG_START]:
                    self.state = 18
                    self.tag()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 23
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
            self.state = 24
            self.match(TagTemplateParser.TAG_START)
            self.state = 25
            self.match(TagTemplateParser.TAG_ID)
            self.state = 26
            self.match(TagTemplateParser.ARG_START)
            self.state = 27
            self.argumentList()
            self.state = 28
            self.match(TagTemplateParser.ARG_END)
            self.state = 33
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==TagTemplateParser.CONTEXT_START:
                self.state = 29
                self.match(TagTemplateParser.CONTEXT_START)
                self.state = 30
                localctx.context = self.pattern()
                self.state = 31
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
            self.state = 44
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [TagTemplateParser.NUMERIC_VALUE, TagTemplateParser.BOOLEAN_VALUE, TagTemplateParser.STRING_START]:
                self.enterOuterAlt(localctx, 1)
                self.state = 35
                self.argument()
                self.state = 40
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==TagTemplateParser.ARG_SEPARATOR:
                    self.state = 36
                    self.match(TagTemplateParser.ARG_SEPARATOR)
                    self.state = 37
                    self.argument()
                    self.state = 42
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

        def BOOLEAN_VALUE(self):
            return self.getToken(TagTemplateParser.BOOLEAN_VALUE, 0)

        def NUMERIC_VALUE(self):
            return self.getToken(TagTemplateParser.NUMERIC_VALUE, 0)

        def stringLiteral(self):
            return self.getTypedRuleContext(TagTemplateParser.StringLiteralContext,0)


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
            self.state = 49
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [TagTemplateParser.BOOLEAN_VALUE]:
                self.enterOuterAlt(localctx, 1)
                self.state = 46
                self.match(TagTemplateParser.BOOLEAN_VALUE)
                pass
            elif token in [TagTemplateParser.NUMERIC_VALUE]:
                self.enterOuterAlt(localctx, 2)
                self.state = 47
                self.match(TagTemplateParser.NUMERIC_VALUE)
                pass
            elif token in [TagTemplateParser.STRING_START]:
                self.enterOuterAlt(localctx, 3)
                self.state = 48
                self.stringLiteral()
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


    class StringLiteralContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING_START(self):
            return self.getToken(TagTemplateParser.STRING_START, 0)

        def STRING_END(self):
            return self.getToken(TagTemplateParser.STRING_END, 0)

        def STRING_VALUE(self):
            return self.getToken(TagTemplateParser.STRING_VALUE, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_stringLiteral

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStringLiteral" ):
                return visitor.visitStringLiteral(self)
            else:
                return visitor.visitChildren(self)




    def stringLiteral(self):

        localctx = TagTemplateParser.StringLiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_stringLiteral)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(TagTemplateParser.STRING_START)
            self.state = 53
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==TagTemplateParser.STRING_VALUE:
                self.state = 52
                self.match(TagTemplateParser.STRING_VALUE)


            self.state = 55
            self.match(TagTemplateParser.STRING_END)
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
        self.enterRule(localctx, 12, self.RULE_rawText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 57
            self.match(TagTemplateParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





