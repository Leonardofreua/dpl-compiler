from TokenType import TokenType
from Context import Context
from symbols import VarSymbol


class TypeChecker:
    def is_allowed_type(self, context: Context, value: VarSymbol) -> bool:
        if context == Context.BIN_OP or Context.UN_OP:
            allowed_types = [TokenType.INTEGER.value, TokenType.REAL.value]

            if value.type.name in allowed_types:
                return True

        return False