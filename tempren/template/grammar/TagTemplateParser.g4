parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

pattern
    : (rawText | tag)* EOF
    ;

tag
    : TAG_START TAG_ID '(' ')'
    ;

rawText
    : TEXT
    ;
