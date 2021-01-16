# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                       Handler                                           #
#                                                                                         #
# This class is the component that processes the executions of the tree nodes (AST), that #
# is, it is here that the direct treatment of operations occurs according to the          #
# classification assigned to each one of the tree nodes. Therefore, if there is a binary  #
# expression or content to be printed on the screen, this is where they will actually be  #
# processed according to their purpose.                                                   #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                         #
#   Author: Leonardo Freua                                                                #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


from typing import Union, Optional

from visitor import NodeVisitor
from token_type import TokenType
from AST import (
    Program,
    Block,
    Compound,
    Assign,
    Var,
    Writeln,
    BinaryOperator,
    UnaryOperator,
    VarDeclaration,
    Type,
    Num,
    String,
    Boolean,
    Empty,
)


class Handler(NodeVisitor):
    """Abstract-Syntax Tree (AST) already processed.

    Args:
        tree (Program): object represeting the root of the tree containing the ramaining
        nodes of the branch
    """

    def __init__(self, tree: Program) -> None:
        self.tree = tree
        self.GLOBAL_MEMORY = {}

    def visit_Program(self, node: Program) -> None:
        """Visit the Block node in AST and call it.

        Args:
            node (Program): Program node (root)
        """

        self.visit(node.block)

    def visit_Block(self, node: Block) -> None:
        """Initializes the method calls according to the nodes represented by the
        variables and compound declarations.

        Args:
            node (Block): the block containing the VAR and BEGIN sections
        """

        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDeclaration(self, node: VarDeclaration) -> None:
        pass

    def visit_Type(self, node: Type) -> None:
        pass

    def visit_BinaryOperator(self, node: BinaryOperator) -> Union[int, float, None]:
        """Performs Binary Operations according to the arithmetic operator.

        Args:
            node (BinaryOperator): node containing the variables (or numbers) and the
            arithmetic operators

        Returns:
            Union[int, float, None]: result of the arithmetic operation
        """

        if node.operator.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.operator.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.operator.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.operator.type == TokenType.INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.operator.type == TokenType.FLOAT_DIV:
            return float(self.visit(node.left)) / float(self.visit(node.right))

        return None

    def visit_UnaryOperator(self, node: UnaryOperator) -> Optional[int]:
        """Performs Unary Operations according to the arithmetic operator (PLUS and MINUS).

        Args:
            node (UnaryOperator): node containing the variables (or numbers) and the
            arithmetic operators (PLUS and MINUS)

        Returns:
            Optional[int]: result of the arithmetic operation
        """

        operator = node.operator.type
        if operator == TokenType.PLUS:
            return +self.visit(node.expression)
        elif operator == TokenType.MINUS:
            return -self.visit(node.expression)

        return None

    def visit_Num(self, node: Num) -> int:
        """Returns a number (contant) of the a tree node.

        Args:
            node (Num): a token represeting a number (constant)

        Returns:
            int: an integer number
        """

        return node.value

    def visit_String(self, node: String) -> str:
        """Returns a string (literal) of the a tree node.

        Args:
            node (String): a token represeting a string (literal)

        Returns:
            str: a string (literal)
        """

        return node.value

    def visit_Boolean(self, node: Boolean) -> bool:
        """Returns a bool (literal) of the a tree node.

        Args:
            nodo (Boolean): a token represeting a literal boolean type

        Returns:
            bool: a bool (literal)
        """

        return node.value

    def visit_Compound(self, node: Compound) -> None:
        """Central component that coordinates the compound statements (assigments and
        writeln statement) and calls the methods according to their type.

        Args:
            node (Compound): node containing all of the compound statements (assigments
            and writeln statement)
        """

        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node: Assign) -> None:
        """allocates in a dictionary the content of an assignment (value) according to
        the variable to which it is being assigned (key).

        Args:
            node (Assign): node containing a assigment statement content
        """

        var_name = node.left.value
        var_value = self.visit(node.right)
        self.GLOBAL_MEMORY[var_name] = var_value

    def visit_Var(self, node: Var) -> Union[int, str, None]:
        """Search the variable in the dictionary memory and verify if it exists, if not
        found shows an error stating has not been declared.

        Args:
            node (Var): a node containing a variable

        Returns:
            Union[int, str, None]: content of the a variable.
        """

        var_name = node.value
        value = self.GLOBAL_MEMORY.get(var_name)

        return value

    def visit_Writeln(self, node: Writeln) -> None:
        """Prints content on the screen according to what was passed in the command
        writeln.

        Args:
            node (Writeln): content passed in the command writeln
        """

        print(self.visit(node.content[0]))

    def visit_Empty(self, node: Empty) -> None:
        pass

    def handle(self) -> Union[str, int]:
        """Starts scanning the tree nodes.

        Returns:
            Union[str, int]: results of the arithmetic operations the content present
            in the command writeln.
        """

        tree = self.tree

        if tree is None:
            return ""
        return self.visit(tree)
