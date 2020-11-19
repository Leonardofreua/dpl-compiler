# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                 List of token types                                     #
#                                                                                         #
# Below is the list of tokens and their respective types accepted by the current grammar  #
# of the LPD language.                                                                    #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                         #
#   Author: Leonardo Freua                                                                #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from enum import Enum


class TokenType(Enum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    FLOAT_DIV = "/"
    LPAREN = "("
    RPAREN = ")"
    SEMI = ";"
    DOT = "."
    COLON = ":"
    COMMA = ","
    HYPHEN = "-"
    UNDER_SCORE = "_"
    AT_SIGN = "@"
    EXCLAMATION = "!"
    DOLLAR = "$"
    HASH = "#"
    PERCENTAGE = "%"
    AMPERSAND = "&"
    EQUAL = "="
    DIACRITIC = "¨"
    PIPE = "|"
    QUESTION_MARK = "?"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LBRACKET = "["
    RBRACKET = "]"
    TILDE = "~"
    CIRCUMFLEX = "^"
    LBRACE = "{"
    RBRACE = "}"

    PROGRAM = "PROGRAMA"
    INTEGER = "INTEIRO"
    STRING = "STRING"
    BOOLEAN = "BOOLEANO"
    TRUE = "VERDADEIRO"
    FALSE = "FALSO"
    REAL = "REAL"
    INTEGER_DIV = "DIV"
    VAR = "VAR"
    BEGIN = "INICIO"
    WRITELN = "ESCREVA"
    END = "FIM"

    ID = "ID"
    INTEGER_CONST = "INTEGER_CONST"
    REAL_CONST = "REAL_CONST"
    STRING_CONST = "STRING_CONST"
    ASSIGN = ":="
    EOF = "EOF"
