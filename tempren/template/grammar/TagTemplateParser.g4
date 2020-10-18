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
    : TAG_START TAG_ID argumentList ('{' context=pattern '}')?
    ;

argumentList
    : '(' ')'
    ;

tagContext
    : '{' pattern '}'
    ;

rawText
    : TEXT
    ;
