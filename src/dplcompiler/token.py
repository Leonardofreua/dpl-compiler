# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                          Token                          #
#                                                         #
# This is where the default token structure is set up.    #
#                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                         #
#   Author: Leonardo Freua                                #
#                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


from typing import Any, Optional, Union


class Token:
    """This class represents the Token (atom) extracted from the source code.

    Args:
        type (Any): extracted token type
        value (Union[str, float, int, None]): extracted character
        line (Optional[int], optional): line where the token is. Defaults to None.
        column (Optional[int], optional): column where the token is. Defaults to None.
    """

    def __init__(
        self,
        type: Any,
        value: Union[str, float, int, None],
        line: Optional[int] = None,
        column: Optional[int] = None,
    ):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3, line=1, column=4)
            Token(PLUS, '+', position:1:4)

        Returns:
            str: token description
        """
        return f"Token({self.type}, {repr(self.value)}, position={self.line}:{self.column})"

    def __repr__(self):
        return self.__str__()
