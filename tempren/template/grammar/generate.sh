#!/usr/bin/env bash
function antlr4() {
  export CLASSPATH="/usr/local/lib/antlr-4.10.1-complete.jar:$CLASSPATH"
  java org.antlr.v4.Tool "$@"
}

antlr4 -Dlanguage=Python3 TagTemplateLexer.g4
antlr4 -Dlanguage=Python3 -visitor -no-listener TagTemplateParser.g4
