from typing import NoReturn

from Token import Token
from exceptions import ErrorCode, TokenizeError, ParserError, SemanticError


class TokenizerErrorHandler:
    @classmethod
    def error(cls, current_char: str, line: int, column: int) -> NoReturn:
        raise TokenizeError(
            message=f"Tokenize error on {current_char} **line: {line} **column: {column}"
        )


class ParserErrorHandler:
    @classmethod
    def error(cls, error_code: ErrorCode, token: Token) -> NoReturn:
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f"{error_code.value} \n\t{token}",
        )


class SemanticErrorHandler:
    @classmethod
    def error(cls, error_code: ErrorCode, token: Token, var_name: str) -> NoReturn:
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f"{error_code.value} \n \t{token} \n \tIdentifier: '{var_name}'",
        )

    @classmethod
    def type_error(cls, *args, token: Token) -> NoReturn:
        formatted_variable_types = (
            " and ".join(args) if len(args) == 2 else ", ".join(args)
        )
        raise SemanticError(
            error_code=ErrorCode.TYPE_ERROR,
            token=token,
            message=f"{ErrorCode.TYPE_ERROR.value}: {formatted_variable_types}\n \t{token}",
        )
