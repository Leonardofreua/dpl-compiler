import llvmlite.ir as ir

from TokenType import TokenType
from visitor import NodeVisitor
from symbols import VarSymbol
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

# from exceptions import CodeGeneratorErrorHandler


class CodeGenerator(NodeVisitor):
    def __init__(self, symbol_table) -> None:

        # Module is an LLVM construct that contains functions and global variables.
        # In many ways, it is the top-level structure that the LLVM IR uses to contain
        # code. It will own the memory for all of the IR that we generate, which is why
        # the codegen() method returns a raw Value*, rather than a unique_ptr<Value>.
        self.module = ir.Module()

        # The Builder object is a helper object that makes it easy to generate LLVM
        # instructions. Instances of the IRBuilder class template keep track of the
        # current place to insert instructions and has methods to create new instructions.
        self.builder = None
        self.symbol_table = symbol_table
        self.expr_counter = 0
        self.str_counter = 0
        self.bool_counter = 0
        self.func_name = ""
        self.GLOBAL_MEMORY = {}

    def _create_instruct(self, typ: str) -> None:
        if typ == 'String':
            self.str_counter += 1
            self.func_name = f"_{typ}.{self.str_counter}"
            func_type = ir.FunctionType(ir.VoidType(), [])

            # fmt = "%s\n\0"
            # c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
            #                     bytearray(fmt.encode("utf8")))
            # global_fmt = ir.GlobalVariable(
            #     self.module, c_fmt.type, name="fstr")
            # global_fmt.linkage = 'internal'
            # global_fmt.global_constant = True
            # global_fmt.initializer = c_fmt
        elif typ == 'Boolean':
            self.bool_counter += 1
            self.func_name = f"_{typ}.{self.bool_counter}"
            func_type = ir.FunctionType(ir.IntType(1), [])
        else:
            self.expr_counter += 1
            self.func_name = f"_{typ}_Expr.{self.expr_counter}"
            func_type = ir.FunctionType(ir.DoubleType(), [])

        main_func = ir.Function(self.module, func_type, self.func_name)
        bb_entry = main_func.append_basic_block("entry")
        self.builder = ir.IRBuilder(bb_entry)

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
        """Search the variable of the assigment in the Symbol Table and verify if it exists,
        if found triggers the next symbol (if it exists), else show an error stating that
        the variable has not been declared.

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

        if node.right is not None and not isinstance(
            node.right, (UnaryOperator, BinaryOperator)
        ):
            self.GLOBAL_MEMORY[node.left.value] = instruct

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.symbol_table.get_token(var_name)
        var_symbol.type = ir.DoubleType()

        return var_symbol

    def visit_Num(self, node):
        return ir.Constant(ir.DoubleType(), float(node.value))

    def visit_BinaryOperator(self, node):
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
        else:
            print("Unknown binary operator")
            # raise CodeGeneratorErrorHandler(
            #     node.operator.type, "Unknown binary operator"
            # )

    def visit_String(self, node: String) -> str:
        """Returns a string (literal) of the a tree node.

        Args:
            node (String): a token represeting a string (literal)

        Returns:
            str: a string (literal)
        """

        content = node.value
        return ir.Constant(
            ir.ArrayType(ir.IntType(8), len(content)), bytearray(
                content.encode("utf8"))
        )

    def visit_Boolean(self, node: Boolean) -> bool:
        """Returns a bool (literal) of the a tree node.

        Args:
            nodo (Boolean): a token represeting a literal boolean type

        Returns:
            bool: a bool (literal)
        """

        if node.token.type == TokenType.FALSE:
            return ir.Constant(ir.IntType(1), 0)
        else:
            return ir.Constant(ir.IntType(1), 1)

    def visit_Writeln(self, node: Writeln) -> None:
        """Prints content on the screen according to what was passed in the command
        escreva.

        Args:
            node (Writeln): content passed in the command escreva
        """

        # voidptr_ty = ir.IntType(8).as_pointer()
        # fmt_arg = builder.bitcast(global_fmt, voidptr_ty) #creates the %".4" variable with the point pointing to the fstr
        # builder.call(printf, [fmt_arg, c_str]) #We are calling the prinf function with the fmt and arg and returning the value as defiend on the next line
        # builder.ret_void()

        for content in node.content:
            print(self.visit(content))

    def visit_VarDeclaration(self, node: VarDeclaration) -> None:
        pass

    def visit_Type(self, node: Type) -> None:
        pass

    def visit_Empty(self, node: Empty) -> None:
        pass
