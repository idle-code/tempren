#!/usr/bin/env bash
export CLASSPATH="/usr/local/lib/antlr-4.8-complete.jar:$CLASSPATH"
alias antlr4="java org.antlr.v4.Tool"
antlr4 -Dlanguage=Python3 TagExpression.g4

