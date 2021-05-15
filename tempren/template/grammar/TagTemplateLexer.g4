lexer grammar TagTemplateLexer;

fragment ID
    : (LETTER | '_') (LETTER | NUMBER_CHAR | '_')*
    ;

fragment LETTER
    : [a-zA-Z]
    ;

fragment NUMBER_CHAR
    : [0-9]
    ;

GLOBAL_WHITESPACE
    : [\t\n\r] -> skip
    ;

TAG_START
    : '%' -> skip, mode(TAG_MODE)
    ;

PIPE
    : '|'
    ;

TEXT
    : ('\\{' | '\\}' | '\\|' | ~[%{}|\t\n\r])+
    ;

CONTEXT_START
    : '{'
    ;

CONTEXT_END
    : '}'
    ;

ANY
    : .
    ;

mode TAG_MODE;

TAG_WHITESPACE
    : [\t\n\r] -> skip
    ;

ARGS_START
    : '(' -> skip, mode(ARGS_MODE)
    ;

TAG_ID
    : ID
    ;


mode ARGS_MODE;

ARGS_WHITESPACE
    : [ \t\n\r] -> skip
    ;

ARG_END
    : ')' -> skip, mode(DEFAULT_MODE)
    ;

ARG_SEPARATOR
    : ',' -> skip
    ;

NUMERIC_VALUE
    : '-'? NUMBER_CHAR+
    ;

BOOLEAN_VALUE
    : [Tt] 'rue'
    | [Ff] 'alse'
    ;

STRING_VALUE
    : '\'' ('\\\'' | ~['])* '\''
    | '"' ('\\"' | ~["])* '"'
    ;

ARG_NAME
    : ID
    ;

ARG_EQUALS
    : '='
    ;
