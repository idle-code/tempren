lexer grammar TagTemplateLexer;

TAG_START
    : '%' -> pushMode(TAG_MODE)
    ;
TEXT
    : ~('%')+
    ;

fragment INVALID_WHITESPACE_CHAR
    : [\t\n\r]
    ;

// CHECK: will INVALID_WHITESPACE work in other modes too?
INVALID_WHITESPACE
    : INVALID_WHITESPACE_CHAR -> skip
    ;

mode TAG_MODE;

ARG_START
    : '('
    ;

ARG_END_CONTEXT_START
    : '){' -> popMode
    ;

ARG_END
    : ')' -> popMode
    ;

CONTEXT_END
    : '}'
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
