# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                           Definition of symbols                         #
#                                                                         #
# Below are defined the types of symbols accepted by the DPL language     #
# (so far) together with their acceptance parameters.                     #
#                                                                         #
#                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                         #
#   Author: Leonardo Freua                                                #
#                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from typing import Optional


class Symbol:
    def __init__(
        self, name, type=None
    ):  # type: (str, Optional[BuiltinTypeSymbol]) -> None
        self.name = name
        self.type = type


class BuiltinTypeSymbol(Symbol):
    """Primitive type stamp.

    Args:
        name (str): primitive type name:INTEGER,
                                        REAL,
                                        STRING,
                                        BOOLEAN
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>(name='{self.name}')"


class VarSymbol(Symbol):
    """Set of variables settings.

    Args:
        name (str): variable name
        type (Optional[BuiltinTypeSymbol]): variable type object.
    """

    def __init__(self, name, type):  # type: (str, Optional[BuiltinTypeSymbol]) -> None
        super().__init__(name, type)

    def __str__(self):
        return f"<{self.__class__.__name__}>(name='{self.name}', type='{self.type}')"

    __repr__ = __str__
