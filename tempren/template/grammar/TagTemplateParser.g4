parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

rootPattern
    : pattern EOF
    ;

tag
    : TAG_START TAG_ID argumentList ('{' pattern '}')?
    ;

pipeList
    : (PIPE tag)+
    ;

pattern
    : (rawText | tag)* pipe_list=pipeList?
    ;

argumentList
    : ARGS_START ARGS_END
    | ARGS_START argument (ARG_SEPARATOR argument)* ARGS_END
    ;

argument
    : ARG_NAME '=' argumentValue
    | ARG_NAME
    | argumentValue
    ;

argumentValue
    : BOOLEAN_VALUE
    | NUMERIC_VALUE
    | STRING_VALUE
    ;

rawText
    : TEXT
    ;
