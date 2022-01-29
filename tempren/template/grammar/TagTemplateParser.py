# Generated from TagTemplateParser.g4 by ANTLR 4.9.2
# encoding: utf-8
import sys
from io import StringIO

from antlr4 import *

if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\24")
        buf.write("]\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5")
        buf.write("\3\35\n\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3'\n\3\3")
        buf.write("\4\3\4\6\4+\n\4\r\4\16\4,\3\5\3\5\7\5\61\n\5\f\5\16\5")
        buf.write("\64\13\5\3\5\5\5\67\n\5\3\6\3\6\3\6\3\6\3\6\3\6\7\6?\n")
        buf.write("\6\f\6\16\6B\13\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\7\6K\n\6")
        buf.write("\f\6\16\6N\13\6\5\6P\n\6\3\7\3\7\3\7\3\7\3\7\5\7W\n\7")
        buf.write("\3\b\3\b\3\t\3\t\3\t\2\2\n\2\4\6\b\n\f\16\20\2\3\3\2\20")
        buf.write("\22\2b\2\22\3\2\2\2\4&\3\2\2\2\6*\3\2\2\2\b\62\3\2\2\2")
        buf.write("\nO\3\2\2\2\fV\3\2\2\2\16X\3\2\2\2\20Z\3\2\2\2\22\23\5")
        buf.write("\b\5\2\23\24\7\2\2\3\24\3\3\2\2\2\25\26\7\4\2\2\26\27")
        buf.write("\7\f\2\2\27\34\5\n\6\2\30\31\7\7\2\2\31\32\5\b\5\2\32")
        buf.write("\33\7\b\2\2\33\35\3\2\2\2\34\30\3\2\2\2\34\35\3\2\2\2")
        buf.write("\35'\3\2\2\2\36\37\7\4\2\2\37'\7\f\2\2 !\7\4\2\2!\"")
        buf.write("\7\f\2\2\"#\5\n\6\2#$\7\7\2\2$%\5\b\5\2%'\3\2\2\2&\25")
        buf.write("\3\2\2\2&\36\3\2\2\2& \3\2\2\2'\5\3\2\2\2()\7\5\2\2)")
        buf.write("+\5\4\3\2*(\3\2\2\2+,\3\2\2\2,*\3\2\2\2,-\3\2\2\2-\7\3")
        buf.write("\2\2\2.\61\5\20\t\2/\61\5\4\3\2\60.\3\2\2\2\60/\3\2\2")
        buf.write("\2\61\64\3\2\2\2\62\60\3\2\2\2\62\63\3\2\2\2\63\66\3\2")
        buf.write("\2\2\64\62\3\2\2\2\65\67\5\6\4\2\66\65\3\2\2\2\66\67\3")
        buf.write("\2\2\2\67\t\3\2\2\289\7\13\2\29P\7\16\2\2:;\7\13\2\2;")
        buf.write("@\5\f\7\2<=\7\17\2\2=?\5\f\7\2><\3\2\2\2?B\3\2\2\2@>\3")
        buf.write("\2\2\2@A\3\2\2\2AC\3\2\2\2B@\3\2\2\2CD\7\16\2\2DP\3\2")
        buf.write("\2\2EP\7\13\2\2FG\7\13\2\2GL\5\f\7\2HI\7\17\2\2IK\5\f")
        buf.write("\7\2JH\3\2\2\2KN\3\2\2\2LJ\3\2\2\2LM\3\2\2\2MP\3\2\2\2")
        buf.write("NL\3\2\2\2O8\3\2\2\2O:\3\2\2\2OE\3\2\2\2OF\3\2\2\2P\13")
        buf.write("\3\2\2\2QR\7\23\2\2RS\7\24\2\2SW\5\16\b\2TW\7\23\2\2U")
        buf.write("W\5\16\b\2VQ\3\2\2\2VT\3\2\2\2VU\3\2\2\2W\r\3\2\2\2XY")
        buf.write("\t\2\2\2Y\17\3\2\2\2Z[\7\6\2\2[\21\3\2\2\2\f\34&,\60\62")
        buf.write("\66@LOV")
        return buf.getvalue()


class TagTemplateParser(Parser):

    grammarFileName = "TagTemplateParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    sharedContextCache = PredictionContextCache()

    literalNames = [
        "<INVALID>",
        "<INVALID>",
        "'%'",
        "'|'",
        "<INVALID>",
        "'{'",
        "'}'",
        "<INVALID>",
        "<INVALID>",
        "'('",
        "<INVALID>",
        "<INVALID>",
        "')'",
        "','",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "'='",
    ]

    symbolicNames = [
        "<INVALID>",
        "GLOBAL_WHITESPACE",
        "TAG_START",
        "PIPE",
        "TEXT",
        "CONTEXT_START",
        "CONTEXT_END",
        "ANY",
        "TAG_WHITESPACE",
        "ARGS_START",
        "TAG_ID",
        "ARGS_WHITESPACE",
        "ARGS_END",
        "ARG_SEPARATOR",
        "NUMERIC_VALUE",
        "BOOLEAN_VALUE",
        "STRING_VALUE",
        "ARG_NAME",
        "ARG_EQUALS",
    ]

    RULE_rootPattern = 0
    RULE_tag = 1
    RULE_pipeList = 2
    RULE_pattern = 3
    RULE_argumentList = 4
    RULE_argument = 5
    RULE_argumentValue = 6
    RULE_rawText = 7

    ruleNames = [
        "rootPattern",
        "tag",
        "pipeList",
        "pattern",
        "argumentList",
        "argument",
        "argumentValue",
        "rawText",
    ]

    EOF = Token.EOF
    GLOBAL_WHITESPACE = 1
    TAG_START = 2
    PIPE = 3
    TEXT = 4
    CONTEXT_START = 5
    CONTEXT_END = 6
    ANY = 7
    TAG_WHITESPACE = 8
    ARGS_START = 9
    TAG_ID = 10
    ARGS_WHITESPACE = 11
    ARGS_END = 12
    ARG_SEPARATOR = 13
    NUMERIC_VALUE = 14
    BOOLEAN_VALUE = 15
    STRING_VALUE = 16
    ARG_NAME = 17
    ARG_EQUALS = 18

    def __init__(self, input: TokenStream, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = ParserATNSimulator(
            self, self.atn, self.decisionsToDFA, self.sharedContextCache
        )
        self._predicates = None

    class RootPatternContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext, 0)

        def EOF(self):
            return self.getToken(TagTemplateParser.EOF, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_rootPattern

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitRootPattern"):
                return visitor.visitRootPattern(self)
            else:
                return visitor.visitChildren(self)

    def rootPattern(self):

        localctx = TagTemplateParser.RootPatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_rootPattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.pattern()
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
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.errorNoArgumentList = None  # Token
            self.errorUnclosedContext = None  # Token

        def TAG_START(self):
            return self.getToken(TagTemplateParser.TAG_START, 0)

        def TAG_ID(self):
            return self.getToken(TagTemplateParser.TAG_ID, 0)

        def argumentList(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentListContext, 0)

        def CONTEXT_START(self):
            return self.getToken(TagTemplateParser.CONTEXT_START, 0)

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext, 0)

        def CONTEXT_END(self):
            return self.getToken(TagTemplateParser.CONTEXT_END, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_tag

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitTag"):
                return visitor.visitTag(self)
            else:
                return visitor.visitChildren(self)

    def tag(self):

        localctx = TagTemplateParser.TagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_tag)
        self._la = 0  # Token type
        try:
            self.state = 36
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 1, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 19
                self.match(TagTemplateParser.TAG_START)
                self.state = 20
                self.match(TagTemplateParser.TAG_ID)
                self.state = 21
                self.argumentList()
                self.state = 26
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la == TagTemplateParser.CONTEXT_START:
                    self.state = 22
                    self.match(TagTemplateParser.CONTEXT_START)
                    self.state = 23
                    self.pattern()
                    self.state = 24
                    self.match(TagTemplateParser.CONTEXT_END)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 28
                self.match(TagTemplateParser.TAG_START)
                self.state = 29
                localctx.errorNoArgumentList = self.match(TagTemplateParser.TAG_ID)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 30
                self.match(TagTemplateParser.TAG_START)
                self.state = 31
                self.match(TagTemplateParser.TAG_ID)
                self.state = 32
                self.argumentList()
                self.state = 33
                localctx.errorUnclosedContext = self.match(
                    TagTemplateParser.CONTEXT_START
                )
                self.state = 34
                self.pattern()
                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PipeListContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PIPE(self, i: int = None):
            if i is None:
                return self.getTokens(TagTemplateParser.PIPE)
            else:
                return self.getToken(TagTemplateParser.PIPE, i)

        def tag(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.TagContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.TagContext, i)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_pipeList

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitPipeList"):
                return visitor.visitPipeList(self)
            else:
                return visitor.visitChildren(self)

    def pipeList(self):

        localctx = TagTemplateParser.PipeListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pipeList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self._errHandler.sync(self)
            _alt = 1
            while _alt != 2 and _alt != ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 38
                    self.match(TagTemplateParser.PIPE)
                    self.state = 39
                    self.tag()

                else:
                    raise NoViableAltException(self)
                self.state = 42
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input, 2, self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PatternContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.pipe_list = None  # PipeListContext

        def rawText(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.RawTextContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.RawTextContext, i)

        def tag(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.TagContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.TagContext, i)

        def pipeList(self):
            return self.getTypedRuleContext(TagTemplateParser.PipeListContext, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_pattern

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitPattern"):
                return visitor.visitPattern(self)
            else:
                return visitor.visitChildren(self)

    def pattern(self):

        localctx = TagTemplateParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 48
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input, 4, self._ctx)
            while _alt != 2 and _alt != ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 46
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [TagTemplateParser.TEXT]:
                        self.state = 44
                        self.rawText()
                        pass
                    elif token in [TagTemplateParser.TAG_START]:
                        self.state = 45
                        self.tag()
                        pass
                    else:
                        raise NoViableAltException(self)

                self.state = 50
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input, 4, self._ctx)

            self.state = 52
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 5, self._ctx)
            if la_ == 1:
                self.state = 51
                localctx.pipe_list = self.pipeList()

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ArgumentListContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.errorUnclosedArgumentList = None  # Token

        def ARGS_START(self):
            return self.getToken(TagTemplateParser.ARGS_START, 0)

        def ARGS_END(self):
            return self.getToken(TagTemplateParser.ARGS_END, 0)

        def argument(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.ArgumentContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.ArgumentContext, i)

        def ARG_SEPARATOR(self, i: int = None):
            if i is None:
                return self.getTokens(TagTemplateParser.ARG_SEPARATOR)
            else:
                return self.getToken(TagTemplateParser.ARG_SEPARATOR, i)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argumentList

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitArgumentList"):
                return visitor.visitArgumentList(self)
            else:
                return visitor.visitChildren(self)

    def argumentList(self):

        localctx = TagTemplateParser.ArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_argumentList)
        self._la = 0  # Token type
        try:
            self.state = 77
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 8, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 54
                self.match(TagTemplateParser.ARGS_START)
                self.state = 55
                self.match(TagTemplateParser.ARGS_END)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 56
                self.match(TagTemplateParser.ARGS_START)
                self.state = 57
                self.argument()
                self.state = 62
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la == TagTemplateParser.ARG_SEPARATOR:
                    self.state = 58
                    self.match(TagTemplateParser.ARG_SEPARATOR)
                    self.state = 59
                    self.argument()
                    self.state = 64
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 65
                self.match(TagTemplateParser.ARGS_END)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 67
                localctx.errorUnclosedArgumentList = self.match(
                    TagTemplateParser.ARGS_START
                )
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 68
                localctx.errorUnclosedArgumentList = self.match(
                    TagTemplateParser.ARGS_START
                )
                self.state = 69
                self.argument()
                self.state = 74
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la == TagTemplateParser.ARG_SEPARATOR:
                    self.state = 70
                    self.match(TagTemplateParser.ARG_SEPARATOR)
                    self.state = 71
                    self.argument()
                    self.state = 76
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ArgumentContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ARG_NAME(self):
            return self.getToken(TagTemplateParser.ARG_NAME, 0)

        def ARG_EQUALS(self):
            return self.getToken(TagTemplateParser.ARG_EQUALS, 0)

        def argumentValue(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentValueContext, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argument

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitArgument"):
                return visitor.visitArgument(self)
            else:
                return visitor.visitChildren(self)

    def argument(self):

        localctx = TagTemplateParser.ArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_argument)
        try:
            self.state = 84
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 9, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 79
                self.match(TagTemplateParser.ARG_NAME)
                self.state = 80
                self.match(TagTemplateParser.ARG_EQUALS)
                self.state = 81
                self.argumentValue()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 82
                self.match(TagTemplateParser.ARG_NAME)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 83
                self.argumentValue()
                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ArgumentValueContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BOOLEAN_VALUE(self):
            return self.getToken(TagTemplateParser.BOOLEAN_VALUE, 0)

        def NUMERIC_VALUE(self):
            return self.getToken(TagTemplateParser.NUMERIC_VALUE, 0)

        def STRING_VALUE(self):
            return self.getToken(TagTemplateParser.STRING_VALUE, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argumentValue

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitArgumentValue"):
                return visitor.visitArgumentValue(self)
            else:
                return visitor.visitChildren(self)

    def argumentValue(self):

        localctx = TagTemplateParser.ArgumentValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_argumentValue)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 86
            _la = self._input.LA(1)
            if not (
                (
                    ((_la) & ~0x3F) == 0
                    and (
                        (1 << _la)
                        & (
                            (1 << TagTemplateParser.NUMERIC_VALUE)
                            | (1 << TagTemplateParser.BOOLEAN_VALUE)
                            | (1 << TagTemplateParser.STRING_VALUE)
                        )
                    )
                    != 0
                )
            ):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RawTextContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self):
            return self.getToken(TagTemplateParser.TEXT, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_rawText

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitRawText"):
                return visitor.visitRawText(self)
            else:
                return visitor.visitChildren(self)

    def rawText(self):

        localctx = TagTemplateParser.RawTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_rawText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 88
            self.match(TagTemplateParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
