parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

rootPattern
    : patternExpression EOF
    ;

tag
    : TAG_ID argumentList '{' patternExpression '}'
    ;

contextlessTag
    : TAG_ID argumentList
    ;

patternExpression
    : pattern pipeList?
    ;

pipeList
    : (PIPE contextlessTag)+
    ;

pattern
    : (rawText | tag | contextlessTag)*
    ;

argumentList
    : argument+
    |
    ;

argument
    : (ARG_NAME '=')? argumentValue
    | ARG_NAME
    ;

argumentValue
    : BOOLEAN_VALUE
    | NUMERIC_VALUE
    | STRING_VALUE
    ;

rawText
    : TEXT
    ;
