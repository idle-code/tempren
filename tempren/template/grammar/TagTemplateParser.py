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
        buf.write("I\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\4\n\t\n\4\13\t\13\3\2\3\2\3\2\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\4\3\4\3\4\3\5\3\5\5\5%\n\5\3\6\3\6\6\6")
        buf.write(")\n\6\r\6\16\6*\3\7\3\7\3\7\7\7\60\n\7\f\7\16\7\63\13")
        buf.write("\7\3\b\6\b\66\n\b\r\b\16\b\67\3\b\5\b;\n\b\3\t\3\t\5\t")
        buf.write("?\n\t\3\t\3\t\5\tC\n\t\3\n\3\n\3\13\3\13\3\13\2\2\f\2")
        buf.write("\4\6\b\n\f\16\20\22\24\2\3\3\2\20\22\2G\2\26\3\2\2\2\4")
        buf.write('\31\3\2\2\2\6\37\3\2\2\2\b"\3\2\2\2\n(\3\2\2\2\f\61\3')
        buf.write("\2\2\2\16:\3\2\2\2\20B\3\2\2\2\22D\3\2\2\2\24F\3\2\2\2")
        buf.write("\26\27\5\b\5\2\27\30\7\2\2\3\30\3\3\2\2\2\31\32\7\f\2")
        buf.write("\2\32\33\5\16\b\2\33\34\7\7\2\2\34\35\5\b\5\2\35\36\7")
        buf.write("\b\2\2\36\5\3\2\2\2\37 \7\f\2\2 !\5\16\b\2!\7\3\2\2\2")
        buf.write('"$\5\f\7\2#%\5\n\6\2$#\3\2\2\2$%\3\2\2\2%\t\3\2\2\2&')
        buf.write("'\7\5\2\2')\5\6\4\2(&\3\2\2\2)*\3\2\2\2*(\3\2\2\2*+")
        buf.write("\3\2\2\2+\13\3\2\2\2,\60\5\24\13\2-\60\5\4\3\2.\60\5\6")
        buf.write("\4\2/,\3\2\2\2/-\3\2\2\2/.\3\2\2\2\60\63\3\2\2\2\61/\3")
        buf.write("\2\2\2\61\62\3\2\2\2\62\r\3\2\2\2\63\61\3\2\2\2\64\66")
        buf.write("\5\20\t\2\65\64\3\2\2\2\66\67\3\2\2\2\67\65\3\2\2\2\67")
        buf.write("8\3\2\2\28;\3\2\2\29;\3\2\2\2:\65\3\2\2\2:9\3\2\2\2;\17")
        buf.write("\3\2\2\2<=\7\23\2\2=?\7\24\2\2><\3\2\2\2>?\3\2\2\2?@\3")
        buf.write("\2\2\2@C\5\22\n\2AC\7\23\2\2B>\3\2\2\2BA\3\2\2\2C\21\3")
        buf.write("\2\2\2DE\t\2\2\2E\23\3\2\2\2FG\7\6\2\2G\25\3\2\2\2\n$")
        buf.write("*/\61\67:>B")
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
    RULE_tag = 1
    RULE_contextlessTag = 2
    RULE_patternExpression = 3
    RULE_pipeList = 4
    RULE_pattern = 5
    RULE_argumentList = 6
    RULE_argument = 7
    RULE_argumentValue = 8
    RULE_rawText = 9

    ruleNames = [
        "rootPattern",
        "tag",
        "contextlessTag",
        "patternExpression",
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

        def patternExpression(self):
            return self.getTypedRuleContext(
                TagTemplateParser.PatternExpressionContext, 0
            )

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
            self.state = 20
            self.patternExpression()
            self.state = 21
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

        def TAG_ID(self):
            return self.getToken(TagTemplateParser.TAG_ID, 0)

        def argumentList(self):
            return self.getTypedRuleContext(TagTemplateParser.ArgumentListContext, 0)

        def CONTEXT_START(self):
            return self.getToken(TagTemplateParser.CONTEXT_START, 0)

        def patternExpression(self):
            return self.getTypedRuleContext(
                TagTemplateParser.PatternExpressionContext, 0
            )

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
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 23
            self.match(TagTemplateParser.TAG_ID)
            self.state = 24
            self.argumentList()
            self.state = 25
            self.match(TagTemplateParser.CONTEXT_START)
            self.state = 26
            self.patternExpression()
            self.state = 27
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
        self.enterRule(localctx, 4, self.RULE_contextlessTag)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.match(TagTemplateParser.TAG_ID)
            self.state = 30
            self.argumentList()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PatternExpressionContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pattern(self):
            return self.getTypedRuleContext(TagTemplateParser.PatternContext, 0)

        def pipeList(self):
            return self.getTypedRuleContext(TagTemplateParser.PipeListContext, 0)

        def getRuleIndex(self):
            return TagTemplateParser.RULE_patternExpression

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitPatternExpression"):
                return visitor.visitPatternExpression(self)
            else:
                return visitor.visitChildren(self)

    def patternExpression(self):

        localctx = TagTemplateParser.PatternExpressionContext(
            self, self._ctx, self.state
        )
        self.enterRule(localctx, 6, self.RULE_patternExpression)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 32
            self.pattern()
            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == TagTemplateParser.PIPE:
                self.state = 33
                self.pipeList()

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
            return TagTemplateParser.RULE_pipeList

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitPipeList"):
                return visitor.visitPipeList(self)
            else:
                return visitor.visitChildren(self)

    def pipeList(self):

        localctx = TagTemplateParser.PipeListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_pipeList)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 38
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 36
                self.match(TagTemplateParser.PIPE)
                self.state = 37
                self.contextlessTag()
                self.state = 40
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
        self.enterRule(localctx, 10, self.RULE_pattern)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == TagTemplateParser.TEXT or _la == TagTemplateParser.TAG_ID:
                self.state = 45
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input, 2, self._ctx)
                if la_ == 1:
                    self.state = 42
                    self.rawText()
                    pass

                elif la_ == 2:
                    self.state = 43
                    self.tag()
                    pass

                elif la_ == 3:
                    self.state = 44
                    self.contextlessTag()
                    pass

                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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
        self.enterRule(localctx, 12, self.RULE_argumentList)
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
        self.enterRule(localctx, 14, self.RULE_argument)
        self._la = 0  # Token type
        try:
            self.state = 64
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 7, self._ctx)
            if la_ == 1:
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
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 63
                self.match(TagTemplateParser.ARG_NAME)
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
        self.enterRule(localctx, 16, self.RULE_argumentValue)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
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
        self.enterRule(localctx, 18, self.RULE_rawText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(TagTemplateParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
