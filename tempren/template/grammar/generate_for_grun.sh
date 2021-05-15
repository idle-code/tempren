#!/usr/bin/env bash
function antlr4() {
  export CLASSPATH="/usr/local/lib/antlr-4.9.2-complete.jar:$CLASSPATH"
  java org.antlr.v4.Tool "$@"
}

antlr4 TagTemplateLexer.g4
javac TagTemplateLexer.java
antlr4 -visitor TagTemplateParser.g4
javac TagTemplateParser.java
