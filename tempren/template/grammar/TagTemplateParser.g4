parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

rootPattern
    : pattern EOF
    ;

pattern
    : (rawText | tag)*
    ;

tag
    : TAG_ID argumentList ('{' context=pattern '}')?
    ;

argumentList
    : argument+
    |
    ;

argument
    : (ARG_NAME '=')? argumentValue
    ;

argumentValue
    : BOOLEAN_VALUE
    | NUMERIC_VALUE
    | STRING_VALUE
    ;

rawText
    : TEXT
    ;
