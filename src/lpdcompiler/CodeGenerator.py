# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                               LLVM IR Code Generator                                    #
#                                                                                         #
# Here the AST is Scanned and Transformed into LLVM IR. The processed AST code is         #
# already Semantically validated.                                                         #
#                                                                                         #
# The code conversion process was carried out following the instructions in the LLVM      #
# documentation. Below the links of the related documentation:                            #
#                                                                                         #
# Kaleidoscope: Code generation to LLVM IR:                                               #
# https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl03.html                  #
#                                                                                         #
# LLVM Language Reference Manual:                                                         #
# https://llvm.org/docs/LangRef.html                                                      #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                         #
#   Author: Leonardo Freua                                                                #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from llvmlite.ir import (
    Constant,
    Instruction,
    Module,
    IRBuilder,
    VoidType,
    IntType,
    DoubleType,
    FunctionType,
    ArrayType,
    GlobalVariable,
    Function,
)

from TokenType import TokenType
from visitor import NodeVisitor
from symbols import VarSymbol
from AST import (
    Program,
    Block,
    Compound,
    Assign,
    UnaryOperator,
    Var,
    Writeln,
    BinaryOperator,
    VarDeclaration,
    Type,
    Num,
    String,
    Boolean,
    Empty,
)


class CodeGenerator(NodeVisitor):
    def __init__(self, symbol_table) -> None:
        # Module is an LLVM construct that contains functions and global variables.
        # In many ways, it is the top-level structure that the LLVM IR uses to contain
        # code. It will own the memory for all of the IR that we generate, which is why
        # the codegen() method returns a raw Value*, rather than a unique_ptr<Value>.
        self.module = Module()

        # The Builder object is a helper object that makes it easy to generate LLVM
        # instructions. Instances of the IRBuilder class template keep track of the
        # current place to insert instructions and has methods to create new instructions.
        self.builder = None
        self.symbol_table = symbol_table
        self.expr_counter = 0
        self.str_counter = 0
        self.bool_counter = 0
        self.printf_counter = 0
        self.func_name = ""
        self.GLOBAL_MEMORY = {}

    def _create_instruct(self, typ: str, is_printf: bool = False) -> None:
        """Create a new Function instruction and attach it to a new Basic Block Entry.

        Args:
            typ (str): node type.
            is_printf (bool, optional): Defaults to False.
        """

        if is_printf or typ in ["String", "ArrayType"]:
            self.str_counter += 1
            self.func_name = f"_{typ}.{self.str_counter}"
            func_type = FunctionType(VoidType(), [])
        elif typ == "Boolean":
            self.bool_counter += 1
            self.func_name = f"_{typ}.{self.bool_counter}"
            func_type = FunctionType(IntType(1), [])
        else:
            self.expr_counter += 1
            self.func_name = f"_{typ}_Expr.{self.expr_counter}"
            func_type = FunctionType(DoubleType(), [])

        main_func = Function(self.module, func_type, self.func_name)
        bb_entry = main_func.append_basic_block("entry")
        self.builder = IRBuilder(bb_entry)

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
            node (Block): the block containing the VAR and INICIO sections
        """

        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

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
        """Creates the LLVM IR instructions for the expressions, strings or Booleans
        that are assigned to a variable and adds these to a **auxiliary** GLOBAL MEMORY.

        Args:
            node (Assign): node containing the assignment content
        """

        node_type = type(node.right).__name__
        if isinstance(node.right, String):
            self._create_instruct(node_type)
            self.visit(node.left)
            instruct = self.visit(node.right)
            c_str = self.builder.alloca(instruct.type)
            self.builder.store(instruct, c_str)
            self.builder.ret_void()
        else:
            self._create_instruct(node_type)
            self.visit(node.left)
            instruct = self.visit(node.right)
            self.builder.ret(instruct)

        self.GLOBAL_MEMORY[node.left.value] = instruct

    def visit_Var(self, node: Var) -> VarSymbol:
        """Search for the variable in the Symbol Table and define the Double Type.

        Args:
            node (Var): variable token

        Returns:
            VarSymbol: a variable symbol with updated type
        """

        var_name = node.value
        var_symbol = self.symbol_table.get_token(var_name)
        var_symbol.type = DoubleType()

        return var_symbol

    def visit_Num(self, node: Num) -> Constant:
        """Set the Double Type to a specific number.

        Args:
            node (Num): a token represeting a number (constant)

        Returns:
            Constant: a LLVM IR Constant representing the number.
        """
        return Constant(DoubleType(), float(node.value))

    def visit_BinaryOperator(self, node: BinaryOperator) -> Instruction:
        """Performs the Binary arithmetic operations and returns a LLVM IR Instruction
        according to the operation.

        Args:
            node (BinaryOperator): node containing the variables (or numbers) and the
            arithmetic operators

        Returns:
            Instruction: LLVM arithmetic instruction
        """

        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(left, VarSymbol):
            left_symbol = self.GLOBAL_MEMORY[left.name]
        else:
            left_symbol = left

        if isinstance(right, VarSymbol):
            right_symbol = self.GLOBAL_MEMORY[right.name]
        else:
            right_symbol = right

        if node.operator.type == TokenType.PLUS:
            return self.builder.fadd(left_symbol, right_symbol, "addtmp")
        elif node.operator.type == TokenType.MINUS:
            return self.builder.fsub(left_symbol, right_symbol, "subtmp")
        elif node.operator.type == TokenType.MUL:
            return self.builder.fmul(left_symbol, right_symbol, "multmp")
        elif node.operator.type == TokenType.INTEGER_DIV:
            return self.builder.fdiv(left_symbol, right_symbol, "udivtmp")
        elif node.operator.type == TokenType.FLOAT_DIV:
            return self.builder.fdiv(left_symbol, right_symbol, "fdivtmp")

    def visit_UnaryOperator(self, node: UnaryOperator) -> Constant:
        """Performs Unary Operations according to the arithmetic operator (PLUS and MINUS)
        transforming them into a LLVM IR Constant.

        Args:
            node (UnaryOperator): node containing the variables (or numbers) and the
            arithmetic operators (PLUS and MINUS)

        Returns:
            Constant: a LLVM IR Constant representing the number or variable.
        """

        operator = node.operator.type
        if operator == TokenType.PLUS:
            expression = self.visit(node.expression)
            return Constant(DoubleType(), float(+expression.constant))
        elif operator == TokenType.MINUS:
            expression = self.visit(node.expression)
            return Constant(DoubleType(), float(-expression.constant))

    def visit_String(self, node: String) -> Constant:
        """Converts the literal string to an array of characters.

        Args:
            node (String): a token represeting a string (literal)

        Returns:
            Constant: a constant containing a array of characters
        """

        content = node.value
        return Constant(
            ArrayType(IntType(8), len(content)), bytearray(
                content.encode("utf8"))
        )

    def visit_Boolean(self, node: Boolean) -> Constant:
        """Converts the boolean type to an integer (i1) constant.

        Args:
            nodo (Boolean): a token represeting a literal boolean type

        Returns:
            Constant: a constant of type IntType (1) representing the Boolean type:
                1 = True and 0 = False
        """

        if node.token.type == TokenType.FALSE:
            return Constant(IntType(1), 0)
        else:
            return Constant(IntType(1), 1)

    def visit_Writeln(self, node: Writeln) -> None:
        """Converts the contents of the command escreva to LLVM ir code and adds the
        print call to the operating system.

        Args:
            node (Writeln): content passed in the command escreva
        """

        self.printf_counter += 1
        output_operation_type = "%s"

        if isinstance(node.content[0], BinaryOperator):
            self._create_instruct("BinaryOperator", is_printf=True)

        writeln_content = self.visit(node.content[0])

        if isinstance(writeln_content, VarSymbol):
            content = self.GLOBAL_MEMORY[writeln_content.name]
        else:
            content = writeln_content

        content_type = type(content.type).__name__

        if self.builder.block.is_terminated:
            self._create_instruct(typ=content_type, is_printf=True)

        if isinstance(content.type, DoubleType):
            output_operation_type = "%f"

        output_format = f"{output_operation_type}\n\0"
        printf_format = Constant(
            ArrayType(IntType(8), len(output_format)),
            bytearray(output_format.encode("utf8")),
        )

        fstr = GlobalVariable(
            self.module, printf_format.type, name=f"fstr_{self.printf_counter}"
        )
        fstr.linkage = "internal"
        fstr.global_constant = True
        fstr.initializer = printf_format

        writeln_type = FunctionType(IntType(32), [], var_arg=True)
        writeln = Function(
            self.module,
            writeln_type,
            name=f"printf_{content_type}_{self.printf_counter}",
        )

        body = self.builder.alloca(content.type)
        temp_loaded = self.builder.load(body)
        self.builder.store(temp_loaded, body)

        void_pointer_type = IntType(8).as_pointer()
        casted_arg = self.builder.bitcast(fstr, void_pointer_type)
        self.builder.call(writeln, [casted_arg, body])
        self.builder.ret_void()

    def visit_VarDeclaration(self, node: VarDeclaration) -> None:
        pass

    def visit_Type(self, node: Type) -> None:
        pass

    def visit_Empty(self, node: Empty) -> None:
        pass
