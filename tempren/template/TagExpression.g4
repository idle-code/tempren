grammar TagExpression;

pattern
    : (Text | tag)* EOF
    ;
tag
    : '%' TagName '()'
    ;

Text
    : [a-zA-Z0-9 ]+
    ;
TagName
    : TagNameStartCharacter TagNameCharacter*
    ;
fragment TagNameStartCharacter
    : [a-zA-Z_]
    ;
fragment TagNameCharacter
    : TagNameStartCharacter | [0-9]
    ;
WhiteSpace
    : [\t\n\r] -> skip
    ;
