lexer grammar TagTemplateLexer;

// TODO: make INVALID_WHITESPACE work in all modes
INVALID_WHITESPACE
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

ARG_START
    : '('
    ;

ARG_END
    : ')' -> popMode
    ;

TAG_ID
    : ID
    ;

fragment ID
    : (LETTER | '_') (LETTER | NUMBER | '_')*
    ;

fragment LETTER
    : [a-zA-Z]
    ;

fragment NUMBER
    : [0-9]
    ;

// TOOD: create mode for argument list handling?
// TOOD: create mode for string handling strings in argument list
