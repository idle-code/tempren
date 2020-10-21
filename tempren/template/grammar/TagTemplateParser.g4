parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

rootPattern
    : pattern EOF
    ;

pattern
    : (rawText | tag)*
    ;

tag
    //: TAG_START TAG_ID argumentList tagContext?
    : TAG_START TAG_ID '(' argumentList ')' ('{' context=pattern '}')?
    ;

argumentList
    : argument (',' argument)*
    |
    ;

argument
    : BOOLEAN_ARGUMENT
    | NUMERIC_ARGUMENT
    ;

rawText
    : TEXT
    ;
