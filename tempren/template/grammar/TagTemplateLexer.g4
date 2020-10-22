lexer grammar TagTemplateLexer;

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

NUMERIC_VALUE
    : NUMBER_CHAR+
    ;

BOOLEAN_VALUE
    : 'true'
    | 'false'
    ;

STRING_START
    : '\'' -> pushMode(STRING_MODE)
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

mode STRING_MODE;

STRING_VALUE
    : (~('\'' | '\\') | '\\' ('\'' | '\\'))+
    ;

STRING_END
    : '\'' -> popMode
    ;
