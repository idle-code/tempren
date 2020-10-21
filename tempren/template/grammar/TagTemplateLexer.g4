lexer grammar TagTemplateLexer;

// TODO: make WHITESPACE work in all modes
GLOBAL_WHITESPACE
    : [\t\n\r] -> skip
    ;

TAG_START
    : '%' -> pushMode(TAG_MODE)
    ;

CONTEXT_START
    : '{'
    ;

CONTEXT_END
    : '}'
    ;

TEXT
    : ~[%{}\t\n\r]+
    ;

ANY
    : .
    ;

mode TAG_MODE;

TAG_WHITESPACE
    : [ \t\n\r] -> skip
    ;

ARG_START
    : '('
    ;

ARG_END
    : ')' -> popMode
    ;

ARG_SEPARATOR
    : ','
    ;

NUMERIC_ARGUMENT
    : NUMBER_CHAR+
    ;

BOOLEAN_ARGUMENT
    : 'true'
    | 'false'
    ;

TAG_ID
    : ID
    ;

fragment ID
    : (LETTER | '_') (LETTER | NUMBER_CHAR | '_')*
    ;

fragment LETTER
    : [a-zA-Z]
    ;

fragment NUMBER_CHAR
    : [0-9]
    ;

// TOOD: create mode for argument list handling?
// TOOD: create mode for string handling strings in argument list
