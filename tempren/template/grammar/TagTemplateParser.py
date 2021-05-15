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
        buf.write("G\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\4\n\t\n\3\2\3\2\3\2\3\2\3\2\3\2\5\2\33\n")
        buf.write("\2\3\3\3\3\3\3\6\3 \n\3\r\3\16\3!\3\4\3\4\3\4\7\4'\n")
        buf.write("\4\f\4\16\4*\13\4\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\6")
        buf.write("\3\7\6\7\66\n\7\r\7\16\7\67\3\7\5\7;\n\7\3\b\3\b\5\b?")
        buf.write("\n\b\3\b\3\b\3\t\3\t\3\n\3\n\3\n\2\2\13\2\4\6\b\n\f\16")
        buf.write("\20\22\2\3\3\2\20\22\2E\2\32\3\2\2\2\4\34\3\2\2\2\6(\3")
        buf.write("\2\2\2\b+\3\2\2\2\n\61\3\2\2\2\f:\3\2\2\2\16>\3\2\2\2")
        buf.write("\20B\3\2\2\2\22D\3\2\2\2\24\25\5\6\4\2\25\26\7\2\2\3\26")
        buf.write("\33\3\2\2\2\27\30\5\4\3\2\30\31\7\2\2\3\31\33\3\2\2\2")
        buf.write("\32\24\3\2\2\2\32\27\3\2\2\2\33\3\3\2\2\2\34\37\5\6\4")
        buf.write("\2\35\36\7\5\2\2\36 \5\n\6\2\37\35\3\2\2\2 !\3\2\2\2!")
        buf.write("\37\3\2\2\2!\"\3\2\2\2\"\5\3\2\2\2#'\5\22\n\2$'\5\b")
        buf.write("\5\2%'\5\n\6\2&#\3\2\2\2&$\3\2\2\2&%\3\2\2\2'*\3\2\2")
        buf.write("\2(&\3\2\2\2()\3\2\2\2)\7\3\2\2\2*(\3\2\2\2+,\7\f\2\2")
        buf.write(",-\5\f\7\2-.\7\7\2\2./\5\6\4\2/\60\7\b\2\2\60\t\3\2\2")
        buf.write("\2\61\62\7\f\2\2\62\63\5\f\7\2\63\13\3\2\2\2\64\66\5\16")
        buf.write("\b\2\65\64\3\2\2\2\66\67\3\2\2\2\67\65\3\2\2\2\678\3\2")
        buf.write("\2\28;\3\2\2\29;\3\2\2\2:\65\3\2\2\2:9\3\2\2\2;\r\3\2")
        buf.write("\2\2<=\7\23\2\2=?\7\24\2\2><\3\2\2\2>?\3\2\2\2?@\3\2\2")
        buf.write("\2@A\5\20\t\2A\17\3\2\2\2BC\t\2\2\2C\21\3\2\2\2DE\7\6")
        buf.write("\2\2E\23\3\2\2\2\t\32!&(\67:>")
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
        "ARG_END",
        "ARG_SEPARATOR",
        "NUMERIC_VALUE",
        "BOOLEAN_VALUE",
        "STRING_VALUE",
        "ARG_NAME",
        "ARG_EQUALS",
    ]

    RULE_rootPattern = 0
    RULE_pipe = 1
    RULE_pattern = 2
    RULE_tag = 3
    RULE_contextlessTag = 4
    RULE_argumentList = 5
    RULE_argument = 6
    RULE_argumentValue = 7
    RULE_rawText = 8

    ruleNames = [
        "rootPattern",
        "pipe",
        "pattern",
        "tag",
        "contextlessTag",
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
    ARG_END = 12
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

        def pipe(self):
            return self.getTypedRuleContext(TagTemplateParser.PipeContext, 0)

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
            self.state = 24
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 0, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 18
                self.pattern()
                self.state = 19
                self.match(TagTemplateParser.EOF)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 21
                self.pipe()
                self.state = 22
                self.match(TagTemplateParser.EOF)
                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PipeContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.entry_pattern = None  # PatternContext
            self.processing_tags = None  # ContextlessTagContext

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext, 0)

        def PIPE(self, i: int = None):
            if i is None:
                return self.getTokens(TagTemplateParser.PIPE)
            else:
                return self.getToken(TagTemplateParser.PIPE, i)

        def contextlessTag(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(
                    TagTemplateParser.ContextlessTagContext
                )
            else:
                return self.getTypedRuleContext(
                    TagTemplateParser.ContextlessTagContext, i
                )

        def getRuleIndex(self):
            return TagTemplateParser.RULE_pipe

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitPipe"):
                return visitor.visitPipe(self)
            else:
                return visitor.visitChildren(self)

    def pipe(self):

        localctx = TagTemplateParser.PipeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_pipe)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 26
            localctx.entry_pattern = self.pattern()
            self.state = 29
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 27
                self.match(TagTemplateParser.PIPE)
                self.state = 28
                localctx.processing_tags = self.contextlessTag()
                self.state = 31
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la == TagTemplateParser.PIPE):
                    break

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

        def contextlessTag(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(
                    TagTemplateParser.ContextlessTagContext
                )
            else:
                return self.getTypedRuleContext(
                    TagTemplateParser.ContextlessTagContext, i
                )

        def getRuleIndex(self):
            return TagTemplateParser.RULE_pattern

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitPattern"):
                return visitor.visitPattern(self)
            else:
                return visitor.visitChildren(self)

    def pattern(self):

        localctx = TagTemplateParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pattern)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 38
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == TagTemplateParser.TEXT or _la == TagTemplateParser.TAG_ID:
                self.state = 36
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input, 2, self._ctx)
                if la_ == 1:
                    self.state = 33
                    self.rawText()
                    pass

                elif la_ == 2:
                    self.state = 34
                    self.tag()
                    pass

                elif la_ == 3:
                    self.state = 35
                    self.contextlessTag()
                    pass

                self.state = 40
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
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.context = None  # PatternContext

        def TAG_ID(self):
            return self.getToken(TagTemplateParser.TAG_ID, 0)

        def argumentList(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentListContext, 0)

        def CONTEXT_START(self):
            return self.getToken(TagTemplateParser.CONTEXT_START, 0)

        def CONTEXT_END(self):
            return self.getToken(TagTemplateParser.CONTEXT_END, 0)

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_tag

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitTag"):
                return visitor.visitTag(self)
            else:
                return visitor.visitChildren(self)

    def tag(self):

        localctx = TagTemplateParser.TagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_tag)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            self.match(TagTemplateParser.TAG_ID)
            self.state = 42
            self.argumentList()
            self.state = 43
            self.match(TagTemplateParser.CONTEXT_START)
            self.state = 44
            localctx.context = self.pattern()
            self.state = 45
            self.match(TagTemplateParser.CONTEXT_END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ContextlessTagContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TAG_ID(self):
            return self.getToken(TagTemplateParser.TAG_ID, 0)

        def argumentList(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentListContext, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_contextlessTag

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitContextlessTag"):
                return visitor.visitContextlessTag(self)
            else:
                return visitor.visitChildren(self)

    def contextlessTag(self):

        localctx = TagTemplateParser.ContextlessTagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_contextlessTag)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            self.match(TagTemplateParser.TAG_ID)
            self.state = 48
            self.argumentList()
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

        def argument(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(TagTemplateParser.ArgumentContext)
            else:
                return self.getTypedRuleContext(TagTemplateParser.ArgumentContext, i)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argumentList

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitArgumentList"):
                return visitor.visitArgumentList(self)
            else:
                return visitor.visitChildren(self)

    def argumentList(self):

        localctx = TagTemplateParser.ArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_argumentList)
        self._la = 0  # Token type
        try:
            self.state = 56
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [
                TagTemplateParser.NUMERIC_VALUE,
                TagTemplateParser.BOOLEAN_VALUE,
                TagTemplateParser.STRING_VALUE,
                TagTemplateParser.ARG_NAME,
            ]:
                self.enterOuterAlt(localctx, 1)
                self.state = 51
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 50
                    self.argument()
                    self.state = 53
                    self._errHandler.sync(self)
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
                                    | (1 << TagTemplateParser.ARG_NAME)
                                )
                            )
                            != 0
                        )
                    ):
                        break

                pass
            elif token in [
                TagTemplateParser.EOF,
                TagTemplateParser.PIPE,
                TagTemplateParser.TEXT,
                TagTemplateParser.CONTEXT_START,
                TagTemplateParser.CONTEXT_END,
                TagTemplateParser.TAG_ID,
            ]:
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
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def argumentValue(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentValueContext, 0)

        def ARG_NAME(self):
            return self.getToken(TagTemplateParser.ARG_NAME, 0)

        def ARG_EQUALS(self):
            return self.getToken(TagTemplateParser.ARG_EQUALS, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_argument

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitArgument"):
                return visitor.visitArgument(self)
            else:
                return visitor.visitChildren(self)

    def argument(self):

        localctx = TagTemplateParser.ArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_argument)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 60
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == TagTemplateParser.ARG_NAME:
                self.state = 58
                self.match(TagTemplateParser.ARG_NAME)
                self.state = 59
                self.match(TagTemplateParser.ARG_EQUALS)

            self.state = 62
            self.argumentValue()
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
        self.enterRule(localctx, 14, self.RULE_argumentValue)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
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
        self.enterRule(localctx, 16, self.RULE_rawText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.match(TagTemplateParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
