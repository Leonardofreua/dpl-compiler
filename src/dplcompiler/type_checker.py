from token_type import TokenType
from context import Context
from symbols import VarSymbol


class TypeChecker:
    def is_allowed_type(self, context: Context, variable_type: VarSymbol) -> bool:
        if context == Context.BIN_OP or Context.UN_OP:
            allowed_types = [
                TokenType.INTEGER.value,
                TokenType.INTEGER_CONST.value,
                TokenType.REAL.value,
                TokenType.REAL_CONST.value,
            ]

            if variable_type in allowed_types:
                return True

        return False
