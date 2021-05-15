parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

rootPattern
    : pattern EOF
    | pipe EOF
    ;

pipe
    : entry_pattern=pattern (PIPE processing_tags=contextlessTag)+
    ;

pattern
    : (rawText | tag | contextlessTag)*
    ;

tag
    : TAG_ID argumentList '{' context=pattern '}'
    ;

contextlessTag
    : TAG_ID argumentList
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
