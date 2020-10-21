parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

rootPattern
    : pattern EOF
    ;

pattern
    : (rawText | tag)*
    ;

tag
    : TAG_START TAG_ID '(' argumentList ')' ('{' context=pattern '}')?
    ;

argumentList
    : argument (',' argument)*
    |
    ;

argument
    : BOOLEAN_VALUE
    | NUMERIC_VALUE
    | stringLiteral
    ;

stringLiteral
    : STRING_START STRING_VALUE? STRING_END
    ;

rawText
    : TEXT
    ;
