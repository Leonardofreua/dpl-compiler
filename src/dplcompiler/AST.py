# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                          Abstract-Syntax tree (AST)                     #
#                                                                         #
# Below the AST nodes defined together with their acceptance parameters.  #
#                                                                         #
# => Reference: https://docs.python.org/3/library/ast.html                #
#                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                         #
#   Author: Leonardo Freua                                                #
#                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union, List

from token import Token


class AST:
    """Abstract-syntax tree (AST)"""

    pass


class Program(AST):
    """Represents 'program' keyword and will be the root of the tree.

    Args:
        name (str): Program name that is declared after the keyword 'PROGRAM'.
        Example: ldp-program

        block (Block): The block object is compounded of declaration of variables (VAR)
        and the assignments made within 'BEGIN'
    """

    def __init__(self, name: str, block: "Block") -> None:
        self.name = name
        self.block = block


class Block(AST):
    """Holds the declarations and compound statements.

    Args:
        declarations (VarDeclaration): object containing the declaration of variables list

        compound_statement (Compound): object with a list of compound instructions that
        are between 'BEGIN' and 'END'
    """

    def __init__(
        self, declarations: "VarDeclaration", compound_statement: "Compound"
    ) -> None:
        self.declarations = declarations
        self.compound_statement = compound_statement


class VarDeclaration(AST):
    """Represents a declaration of variable.

    Args:
        var_node (Var): represents the variable informations, containing the Token
        object and value.

        type_node (Type): the type of the variable which represents the node in the tree
    """

    def __init__(self, var_node: "Var", type_node: "Type") -> None:
        self.var_node = var_node
        self.type_node = type_node


class Type(AST):
    """Represents a variable type.

    Args:
        token (Token): a specific token: Token(INTEGER, 2) or Token(REAL, 3.14)
    """

    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value


class BinaryOperator(AST):
    """Represents BINARY operations of the AST
    Examples: 2 + 3
              4 - 2
              3 * 4 - 2
              6 / 2 + 2

    Args:
        left (Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None]):
            left number of operation
        operator (Token): arithmetic operators (+, -, *, /)
        right (Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None]):
            right number of operation
    """

    def __init__(
        self, left, operator, right
    ):  # type: (Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None], Token, Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None]) -> None
        self.left = left
        self.token = self.operator = operator
        self.right = right


class UnaryOperator(AST):
    """Represents UNARY operations of the AST
    Examples: 5 -- 2 = 7
              5 + - 2 = 3
              + - 2 = -2

    Args:
        operator (Token): arithmetic operators (+ or -)
        expression (Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None]):
            tree node
    """

    def __init__(
        self, operator, expression
    ):  # type: (Token, Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None]) -> None
        self.token = self.operator = operator
        self.expression = expression


class Num(AST):
    def __init__(self, token: Token) -> None:
        """Represents the INTEGER numbers of the AST

        Args:
            token (Token): a specific token: Token(INTEGER, 2)
        """
        self.token = token
        self.value = token.value


class String(AST):
    def __init__(self, token: Token) -> None:
        """Represents the STRING type of the AST

        Args:
            token (Token): a specific token: Token(STRING, 'test')
        """
        self.token = token
        self.value = token.value


class Boolean(AST):
    def __init__(self, token: Token) -> None:
        """Represents the BOOLEAN type of the AST

        Args:
            token (Token): a specific token: Token(BOOLEAN, TRUE)
            or Token(BOOLEAN, FALSE)
        """
        self.token = token
        self.value = token.value


class Compound(AST):
    """Represents a 'program ... END' block."""

    def __init__(self) -> None:
        self.children: List["Assign"] = []


class Var(AST):
    """The Var node is constructed out of ID token.

    Args:
        token (Token): A specific token.
            Example: Token(TokenType.ID, 'Part11', position=1:17)
    """

    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value


class Assign(AST):
    """Represents the assignment between a variable, the operator ':=' and
    an expression.

    Args:
        left (Var): the variable object, containing the Token informations and value
        operator (Token): token ':=' and it's information from the Token object
        right (Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None]):
            a number that makes up the expression to be assigned to variable
    """

    def __init__(
        self,
        left: Var,
        operator: Token,
        right: Union[Var, Num, Boolean, String, BinaryOperator, UnaryOperator, None],
    ) -> None:
        self.left = left
        self.token = self.operator = operator
        self.right = right


class Writeln(AST):
    """Represents the 'writeln' command.

    Args:
        content (List[Union[Var, Num, String, Boolean, BinaryOperator, UnaryOperator, None]]):
            the 'writeln' content
    """

    def __init__(
        self, content
    ):  # type: (List[Union[Var, Num, String, Boolean, BinaryOperator, UnaryOperator, None]]) -> None
        self.content = content


class Empty(AST):
    """Represents an empty statement"""

    pass
