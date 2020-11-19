# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                   Semantic Handler                                      #
#                                                                                         #
# With the aid of the Visitor Pattern, the class in question visits each of the nodes in  #
# the Abstract-Syntax Tree (AST) and when identifying a symbol that is not in the table,  #
# it includes this one. Therefore, this class IS THE CENTRAL COMPONENT in the management  #
# of the Symbol Table and all SEMANTIC CHECKS.                                            #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                         #
#   Author: Leonardo Freua                                                                #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from typing import NoReturn

from Context import Context
from symbols import SymbolTable, VarSymbol
from Token import Token
from TokenType import TokenType
from TypeChecker import TypeChecker
from visitor import NodeVisitor
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
    Num,
    String,
    Boolean,
    Empty,
)

from exceptions.error import ErrorCode, SemanticError


class SemanticHandler(NodeVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.type_checker = TypeChecker()

    def error(self, error_code: ErrorCode, token: Token, var_name: str) -> NoReturn:
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f"{error_code.value} \n \t{token} \n \tIdentifier: '{var_name}'",
        )

    def type_error(self, token: Token, first_type, second_type) -> NoReturn:
        raise SemanticError(
            error_code=ErrorCode.TYPE_ERROR,
            token=token,
            message=f"{ErrorCode.TYPE_ERROR.value} between {first_type} and {second_type}\n\t{token}",
        )

    def visit_Program(self, node: Program) -> None:
        """Visit the Block node in AST and call it.

        Args:
            node (Program): Program node (root)
        """

        self.visit(node.block)

    def visit_Block(self, node: Block) -> None:
        """Visit the variable declaration section (VAR) and call the visit_VarDeclaration
        method to identify and add the symbols and the Symbol Table. After this, call
        visit_Compound method to handle with the compound statements (assigments).

        Args:
            node (Block): the block containing the VAR and INICIO sections
        """

        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDeclaration(self, node: VarDeclaration) -> None:
        """Var declaration section (VAR), finds and adds symbols in the Symbol Table.

        Args:
            node (VarDeclaration): node containing the variable type and the var_node
            represeting the variable
        """

        type_name = node.type_node.value
        type_symbol = self.symbol_table.get_token(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        if self.symbol_table.get_token(var_name) is not None:
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.var_node.token,
                var_name=var_name,
            )

        self.symbol_table.add_token(var_symbol)

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
        """Search the variable of the assigment in the Symbol Table and verify if it exists,
        if found triggers the next symbol (if it exists), else show an error stating that
        the variable has not been declared.

        Args:
            node (Assign): node containing the assignment content
        """

        self.visit(node.right)
        self.visit(node.left)

    def visit_Var(self, node: Var) -> None:
        """"Search the variable in the Symbol Table and verify if it exists, if not found
        shows an error stating has not been declared.

        Args:
            node (Var): variable token
        """

        var_name = node.value
        var_symbol = self.symbol_table.get_token(var_name)

        if var_symbol is None:
            self.error(
                error_code=ErrorCode.ID_NOT_FOUND, token=node.token, var_name=var_name
            )

    def visit_BinaryOperator(self, node: BinaryOperator) -> None:
        """Calls the methods according to the value of the nodes that are to the left and
        right of the expression.

        Args:
            node (BinaryOperator): node containing the node with binary operations
        """

        self.visit(node.left)
        self.visit(node.right)

        if isinstance(node.left, Var):
            left_symbol = self.symbol_table.get_token(node.left.value)

            if not self.type_checker.is_allowed_type(Context.BIN_OP, left_symbol):
                if node.right.token.type == TokenType.ID:
                    right_symbol = self.symbol_table.get_token(node.right.value)
                    right_var_type = right_symbol.type.name
                else:
                    right_var_type = node.right.token.type.value
                self.type_error(
                    token=node.left.token,
                    first_type=left_symbol.type.name,
                    second_type=right_var_type,
                )

        if isinstance(node.right, Var):
            right_symbol = self.symbol_table.get_token(node.right.value)

            if not self.type_checker.is_allowed_type(Context.BIN_OP, right_symbol):
                if node.left.token.type == TokenType.ID:
                    left_symbol = self.symbol_table.get_token(node.left.value)
                    left_var_type = left_symbol.type.name
                else:
                    left_var_type = node.left.token.type.value
                self.type_error(
                    token=node.right.token,
                    first_type=left_var_type,
                    second_type=right_symbol.type.name,
                )

    def visit_UnaryOperator(self, node: UnaryOperator) -> None:
        """Calls the method that performs the Unary Operations.

        Args:
            node (UnaryOperator): node containing a Unary Operation
        """

        self.visit(node.expression)

    def visit_Writeln(self, node: Writeln) -> None:
        pass

    def visit_Num(self, node: Num) -> None:
        pass

    def visit_String(self, node: String) -> None:
        pass

    def visit_Boolean(self, node: Boolean) -> None:
        pass

    def visit_Empty(self, node: Empty) -> None:
        pass
