parser grammar TagTemplateParser;

options { tokenVocab=TagTemplateLexer; }

rootPattern
    : pattern EOF
    ;

tag
    : TAG_START TAG_ID argumentList ('{' pattern '}')?
    | TAG_START errorNoArgumentList=TAG_ID
    | TAG_START TAG_ID argumentList errorUnclosedContext='{' pattern
    | errorMissingTagId=TAG_START argumentList
    ;

pipeList
    : (PIPE tag)+
    | (PIPE errorNonTagInPipeList=rawText)+
    ;

pattern
    : (rawText | tag)* pipe_list=pipeList?
    ;

argumentList
    : ARGS_START ARGS_END
    | ARGS_START argument (ARG_SEPARATOR argument)* ARGS_END
    | errorUnclosedArgumentList=ARGS_START
    | errorUnclosedArgumentList=ARGS_START argument (ARG_SEPARATOR argument)*
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
