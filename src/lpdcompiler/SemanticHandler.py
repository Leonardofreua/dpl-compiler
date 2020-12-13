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

from Context import Context
from symbols import SymbolTable, VarSymbol
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

from exceptions import SemanticErrorHandler
from exceptions import ErrorCode


class SemanticHandler(NodeVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.type_checker = TypeChecker()
        self.GLOBAL_MEMORY = {}

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
            SemanticErrorHandler.error(
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

        self.visit(node.left)
        self.visit(node.right)

        if node.right is not None and not isinstance(node.right, BinaryOperator):
            while isinstance(node.right, UnaryOperator):
                node.right = node.right.expression

            self.GLOBAL_MEMORY[node.left.value] = node.right.token.type

    def visit_Var(self, node: Var) -> None:
        """"Search the variable in the Symbol Table and verify if it exists, if not found
        shows an error stating has not been declared.

        Args:
            node (Var): variable token
        """

        var_name = node.value
        var_symbol = self.symbol_table.get_token(var_name)

        if var_symbol is None:
            SemanticErrorHandler.error(
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

        # Zero division
        if isinstance(node.right, Num) and node.right.value == 0:
            while isinstance(node.left, UnaryOperator):
                node.left = node.left.expression
            SemanticErrorHandler.error_zero_division(node.left.value)

        if isinstance(node.left, (Var, Boolean, String)):
            left_symbol = self.symbol_table.get_token(node.left.value)

            if left_symbol is None:
                SemanticErrorHandler.type_error(
                    node.left.token.type.name, token=node.left.token
                )

            left_symbol_token = self.GLOBAL_MEMORY[left_symbol.name]
            variable_type_not_allowed = not self.type_checker.is_allowed_type(
                Context.BIN_OP, left_symbol.type.name
            )
            value_type_not_allowed = not self.type_checker.is_allowed_type(
                Context.BIN_OP, left_symbol_token.name
            )

            if variable_type_not_allowed or value_type_not_allowed:
                if node.right.token.type == TokenType.ID:
                    right_symbol = self.symbol_table.get_token(node.right.value)
                    right_var_type = right_symbol.type.name
                else:
                    right_var_type = node.right.token.type.value

                if value_type_not_allowed:
                    left_var_type = left_symbol_token.name
                else:
                    left_var_type = left_symbol.type.name

                SemanticErrorHandler.type_error(
                    left_var_type, right_var_type, token=node.left.token
                )

        if isinstance(node.right, (Var, Boolean, String)):
            right_symbol = self.symbol_table.get_token(node.right.value)

            if right_symbol is None:
                SemanticErrorHandler.type_error(
                    node.right.token.type.name, token=node.right.token
                )

            right_symbol_token = self.GLOBAL_MEMORY[right_symbol.name]
            variable_type_not_allowed = not self.type_checker.is_allowed_type(
                Context.BIN_OP, right_symbol.type.name
            )
            value_type_not_allowed = not self.type_checker.is_allowed_type(
                Context.BIN_OP, right_symbol_token.name
            )

            if variable_type_not_allowed or value_type_not_allowed:
                if node.left.token.type == TokenType.ID:
                    left_symbol = self.symbol_table.get_token(node.left.value)
                    left_var_type = left_symbol.type.name
                else:
                    left_var_type = node.left.token.type.value

                if value_type_not_allowed:
                    right_var_type = right_symbol_token.name
                else:
                    right_var_type = right_symbol.type.name

                SemanticErrorHandler.type_error(
                    left_var_type, right_var_type, token=node.right.token
                )

    def visit_UnaryOperator(self, node: UnaryOperator) -> None:
        """Calls the method that performs the Unary Operations.

        Args:
            node (UnaryOperator): node containing a Unary Operation
        """

        self.visit(node.expression)

        if isinstance(node.expression, (Var, Boolean, String)):
            expr_symbol = self.symbol_table.get_token(node.expression.value)

            if expr_symbol is None:
                SemanticErrorHandler.type_error(
                    node.expression.token.type.name, token=node.expression.token
                )

            if not self.type_checker.is_allowed_type(
                Context.UN_OP, expr_symbol.type.name
            ):
                SemanticErrorHandler.type_error(
                    expr_symbol.type.name, token=node.expression.token
                )

    def visit_Writeln(self, node: Writeln) -> None:
        """Calls the methods according to content type and check if they are valid.

        Args:
            node (Writeln): content passed in the command escreva
        """

        for index, item in enumerate(node.content):
            previous_content = node.content[index - 1]
            if previous_content == item:
                self.visit(item)
            elif isinstance(
                previous_content, (UnaryOperator, BinaryOperator)
            ) and not self.type_checker.is_allowed_type(Context.BIN_OP, item.value):
                node_name = previous_content.__class__.__name__
                SemanticErrorHandler.type_error(
                    node_name, item.token.type.name, token=item.token
                )

    def visit_Num(self, node: Num) -> None:
        pass

    def visit_String(self, node: String) -> None:
        pass

    def visit_Boolean(self, node: Boolean) -> None:
        pass

    def visit_Empty(self, node: Empty) -> None:
        pass
