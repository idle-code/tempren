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
        buf.write("\t\b\4\t\t\t\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5")
        buf.write("\3\35\n\3\3\4\3\4\6\4!\n\4\r\4\16\4\"\3\5\3\5\7\5'\n")
        buf.write("\5\f\5\16\5*\13\5\3\5\5\5-\n\5\3\6\3\6\3\6\3\6\3\6\3\6")
        buf.write("\7\6\65\n\6\f\6\16\68\13\6\3\6\3\6\5\6<\n\6\3\7\3\7\3")
        buf.write("\7\3\7\3\7\5\7C\n\7\3\b\3\b\3\t\3\t\3\t\2\2\n\2\4\6\b")
        buf.write("\n\f\16\20\2\3\3\2\20\22\2I\2\22\3\2\2\2\4\25\3\2\2\2")
        buf.write("\6 \3\2\2\2\b(\3\2\2\2\n;\3\2\2\2\fB\3\2\2\2\16D\3\2\2")
        buf.write("\2\20F\3\2\2\2\22\23\5\b\5\2\23\24\7\2\2\3\24\3\3\2\2")
        buf.write("\2\25\26\7\4\2\2\26\27\7\f\2\2\27\34\5\n\6\2\30\31\7\7")
        buf.write("\2\2\31\32\5\b\5\2\32\33\7\b\2\2\33\35\3\2\2\2\34\30\3")
        buf.write("\2\2\2\34\35\3\2\2\2\35\5\3\2\2\2\36\37\7\5\2\2\37!\5")
        buf.write('\4\3\2 \36\3\2\2\2!"\3\2\2\2" \3\2\2\2"#\3\2\2\2#\7')
        buf.write("\3\2\2\2$'\5\20\t\2%'\5\4\3\2&$\3\2\2\2&%\3\2\2\2'")
        buf.write("*\3\2\2\2(&\3\2\2\2()\3\2\2\2),\3\2\2\2*(\3\2\2\2+-\5")
        buf.write("\6\4\2,+\3\2\2\2,-\3\2\2\2-\t\3\2\2\2./\7\13\2\2/<\7\16")
        buf.write("\2\2\60\61\7\13\2\2\61\66\5\f\7\2\62\63\7\17\2\2\63\65")
        buf.write("\5\f\7\2\64\62\3\2\2\2\658\3\2\2\2\66\64\3\2\2\2\66\67")
        buf.write("\3\2\2\2\679\3\2\2\28\66\3\2\2\29:\7\16\2\2:<\3\2\2\2")
        buf.write(";.\3\2\2\2;\60\3\2\2\2<\13\3\2\2\2=>\7\23\2\2>?\7\24\2")
        buf.write("\2?C\5\16\b\2@C\7\23\2\2AC\5\16\b\2B=\3\2\2\2B@\3\2\2")
        buf.write("\2BA\3\2\2\2C\r\3\2\2\2DE\t\2\2\2E\17\3\2\2\2FG\7\6\2")
        buf.write('\2G\21\3\2\2\2\n\34"&(,\66;B')
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
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 28
                self.match(TagTemplateParser.PIPE)
                self.state = 29
                self.tag()
                self.state = 32
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
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 38
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == TagTemplateParser.TAG_START or _la == TagTemplateParser.TEXT:
                self.state = 36
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [TagTemplateParser.TEXT]:
                    self.state = 34
                    self.rawText()
                    pass
                elif token in [TagTemplateParser.TAG_START]:
                    self.state = 35
                    self.tag()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 40
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 42
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == TagTemplateParser.PIPE:
                self.state = 41
                self.pipeList()

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
            self.state = 57
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 6, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 44
                self.match(TagTemplateParser.ARGS_START)
                self.state = 45
                self.match(TagTemplateParser.ARGS_END)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 46
                self.match(TagTemplateParser.ARGS_START)
                self.state = 47
                self.argument()
                self.state = 52
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la == TagTemplateParser.ARG_SEPARATOR:
                    self.state = 48
                    self.match(TagTemplateParser.ARG_SEPARATOR)
                    self.state = 49
                    self.argument()
                    self.state = 54
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 55
                self.match(TagTemplateParser.ARGS_END)
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
            self.state = 64
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 7, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 59
                self.match(TagTemplateParser.ARG_NAME)
                self.state = 60
                self.match(TagTemplateParser.ARG_EQUALS)
                self.state = 61
                self.argumentValue()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 62
                self.match(TagTemplateParser.ARG_NAME)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 63
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
        self.enterRule(localctx, 14, self.RULE_rawText)
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
