# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                               Parser (Syntactic Analyzer)                               #
#                                                                                         #
# The parser will communicate directly with the Lexical Analyzer (Tokenizer) and with the #
# returned tokens it will set up the Abstract-Syntax Tree (AST). Below are some of the    #
# other actions performed by the parser:                                                  #
#                                                                                         #
#       => Processes arithmetic operations;                                               #
#       => Process the strings;                                                           #
#       => Handling errors related to Unexpected Tokens.                                  #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                         #
#   Author: Leonardo Freua                                                                #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from typing import List, Union

from TokenType import TokenType
from AST import (
    Assign,
    BinaryOperator,
    Block,
    Compound,
    Program,
    Writeln,
    Empty,
    Type,
    UnaryOperator,
    Num,
    String,
    Boolean,
    Var,
    VarDeclaration,
)

from exceptions import ParserErrorHandler
from exceptions import ErrorCode


class Parser:
    def __init__(self, tokenizer) -> None:
        self.tokenizer = tokenizer
        # set current token to the first token taken from the file
        self.current_token = self.tokenizer.get_next_token()

    def consume_token(self, token_type: TokenType) -> None:
        """Compare the current token type with the token_type parameter and if they match
        then the current token is consumed and the next token is assigned to the 
        current_token variable. Otherwise, an error of the type UNEXPECTED_TOKEN is displayed.

        Args:
            token_type (TokenType): the type of token that will be found when reading
            tokens found is the source code

        Raises:
            ParserError: when the passed token is unknown
        """

        if self.current_token.type == token_type:
            self.current_token = self.tokenizer.get_next_token()
        else:
            ParserErrorHandler.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN, token=self.current_token
            )

    def program(self) -> Program:
        """This object represents the program body.

        Grammar: PROGRAMA ::=
                    <variable> SEMI 
                 BLOCK DOT

        Returns:
            Program: Contains the name of the program (Ex.: calcula_expressao) and the 
            Block object containing the source code body.
        """

        self.consume_token(TokenType.PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.consume_token(TokenType.SEMI)
        block_node = self.block()
        program_node = Program(prog_name, block_node)
        self.consume_token(TokenType.DOT)
        return program_node

    def block(self) -> Block:
        """Contains the declaration of variables and compound statement.

        Grammar: VAR ::=
                    <declarations>
                 INICIO
                    <compound_statement>

        Returns:
            Block: Contains the declaration of variables (VAR) and compound statement that
            are within INICIO
        """

        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self) -> List[VarDeclaration]:
        """Assembles a list of all declaration of variables.

        Grammar: VAR ::=
                    (<variable_declaration> SEMI)+
                    | empty

        Returns:
            List[VarDeclaration]: List with all declaration of variables
        """

        declarations = []
        if self.current_token.type == TokenType.VAR:
            self.consume_token(TokenType.VAR)
            while self.current_token.type == TokenType.ID:
                var_declaration = self.variable_declaration()
                declarations.extend(var_declaration)
                self.consume_token(TokenType.SEMI)

        return declarations

    def variable_declaration(self) -> List[VarDeclaration]:
        """Assembles a list of all declaration of variables by TYPE_SPEC.

        Grammar: <variable> ::= ID (COMMA ID)* COLON <type_spec>

        Returns:
            List[VarDeclaration]: List with all declaration of variables by type
        """

        var_nodes = [Var(self.current_token)]
        self.consume_token(TokenType.ID)

        while self.current_token.type == TokenType.COMMA:
            self.consume_token(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.consume_token(TokenType.ID)

        self.consume_token(TokenType.COLON)

        type_node = self.type_spec()
        var_declarations = [
            VarDeclaration(var_node, type_node) for var_node in var_nodes
        ]

        return var_declarations

    def type_spec(self) -> Type:
        """Assembles a Type object with the type of variable and the value.

        Grammar: <type_spec> ::= INTEGER
                                | REAL

        Returns:
            Type: object containing the variable type information
        """

        token = self.current_token
        if self.current_token.type == TokenType.INTEGER:
            self.consume_token(TokenType.INTEGER)
        elif self.current_token.type == TokenType.REAL:
            self.consume_token(TokenType.REAL)
        elif self.current_token.type == TokenType.STRING:
            self.consume_token(TokenType.STRING)
        else:
            self.consume_token(TokenType.BOOLEAN)

        node = Type(token)
        return node

    def compound_statement(self) -> Compound:
        """Assembles a list with all compound statements between INICIO and FIM.

        Grammar: <compound_statement> ::= INICIO <statement_list> FIM

        Returns:
            Compound: an object with a list containing all of compound statements
        """
        self.consume_token(TokenType.BEGIN)
        nodes = self.statement_list()
        self.consume_token(TokenType.END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self) -> List[Assign]:
        """Assembles a list with statements (ASSIGNS).

        Grammar: <statement_list> ::= <statement>
                                    | <statement> SEMI (;) <statement_list>

        Returns:
            List[Assign]: List with all assignments
        """
        node = self.statement()

        results = [node]
        while self.current_token.type == TokenType.SEMI:
            self.consume_token(TokenType.SEMI)
            results.append(self.statement())

        return results

    def statement(self) -> Union[Compound, Assign, Empty]:
        """Assembles a specific statement containing a compound, assignment or
        an empty statement.

        Grammar: <statement> ::= <compound_statement>
                               | <assignment_statement>
                               | empty

        Returns:
            Union[Compound, Assign, Empty]: a node of the tree containing an assignment,
            compound or empty statement
        """

        if self.current_token.type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.WRITELN:
            node = self.writeln_statement()
        elif self.current_token.type == TokenType.ID:
            node = self.assignment_statement()
        else:
            node = self.empty()

        return node

    def writeln_statement(self) -> Writeln:
        """Assembles the 'escreva (Writeln)' command content.

        Grammar: <writeln_statement> ::= <expression>

        Returns:
            Writeln: object containing the expression
        """

        self.consume_token(TokenType.WRITELN)

        if self.current_token.type == TokenType.STRING_CONST:
            content = self.string_parser()
        else:
            content = self.expression_parser()

        node = Writeln(content)

        return node

    def assignment_statement(self) -> Assign:
        """Assembles an Assign object containing an expression.
        Grammar: <variable> ::= ASSIGN <expression>.

        Returns:
            Assign: object containing the expression of assignment statement
        """

        left = self.variable()
        token = self.current_token
        self.consume_token(TokenType.ASSIGN)

        if self.current_token.type == TokenType.STRING_CONST:
            right = self.string_parser()
        elif self.current_token.type == TokenType.FALSE:
            right = self.bool_false_parser()
        elif self.current_token.type == TokenType.TRUE:
            right = self.bool_true_parser()
        else:
            right = self.expression_parser()
        node = Assign(left, token, right)

        return node

    def variable(self) -> Var:
        """A token labeled with type ID (identifies uniqueness) representing the variables and 
        the program name (things that must be unique).

        Grammar: <variable> ::= ID.

        Returns:
            Var: a token object containing the type and value
        """

        node = Var(self.current_token)
        self.consume_token(TokenType.ID)
        return node

    def empty(self) -> Empty:
        """An empty statement"""

        return Empty()

    def factor(self) -> Union[Num, BinaryOperator, UnaryOperator, Var, None]:
        """The factor method performs the orchestration between the arithmetic operations.

        Grammar: PLUS <factor>
                | MINUS <factor>
                | INTEGER_CONST
                | REAL_CONST
                | LPAREN <expression> RPAREN
                | <variable>

        Returns:
            Union[BinaryOperator, UnaryOperator, Num, Var, None]: This can be an 
            UnaryOperator (Ex.: --3, 3 -- 5), a number (Ex.: 1, 2, ...) 
            or an BinaryOperator expression ((x + 7) * y) 
        """

        token = self.current_token
        if token.type == TokenType.PLUS:
            self.consume_token(TokenType.PLUS)
            node = UnaryOperator(token, self.factor())
            return node
        elif token.type == TokenType.MINUS:
            self.consume_token(TokenType.MINUS)
            node = UnaryOperator(token, self.factor())
            return node
        elif token.type == TokenType.INTEGER_CONST:
            self.consume_token(TokenType.INTEGER_CONST)
            return Num(token)
        elif token.type == TokenType.REAL_CONST:
            self.consume_token(TokenType.REAL_CONST)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.consume_token(TokenType.LPAREN)
            node = self.expression_parser()
            self.consume_token(TokenType.RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def term(self) -> Union[Num, BinaryOperator, UnaryOperator, Var, None]:
        """Perform the Binary operations between Multiplication, Integer and Float 
        Division tokens.

        Grammar: <term> ::= <factor> ((MUL | INTEGER_DIV | FLOAT_DIV) <factor>)*

        Returns:
            Union[Num, BinaryOperator, UnaryOperator, Var, None]: a token with the binary 
            operation result
        """

        node = self.factor()
        while self.current_token.type in [
            TokenType.MUL,
            TokenType.INTEGER_DIV,
            TokenType.FLOAT_DIV,
        ]:
            token = self.current_token
            if token.type == TokenType.MUL:
                self.consume_token(TokenType.MUL)
            elif token.type == TokenType.INTEGER_DIV:
                self.consume_token(TokenType.INTEGER_DIV)
            elif token.type == TokenType.FLOAT_DIV:
                self.consume_token(TokenType.FLOAT_DIV)

            node = BinaryOperator(left=node, operator=token, right=self.factor())

        return node

    def expression_parser(self) -> Union[Num, BinaryOperator, UnaryOperator, Var, None]:
        """Arithmetic expression parser.

        Grammar: <expression>   ::= <term> ((PLUS | MINUS) <term>)*
                 <term>         ::= <factor> ((MUL | DIV) <factor>)*
                 <factor>       ::= INTEGER | LPAREN <expression> RPAREN

        Returns:
            Union[Num, BinaryOperator, UnaryOperator, Var, None]: a result assignment 
            to a variable, this is can be a number, binary or unary operation or another
            variable 
        """

        node = self.term()
        while self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.consume_token(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.consume_token(TokenType.MINUS)

            node = BinaryOperator(left=node, operator=token, right=self.term())

        return node

    def string_parser(self) -> String:
        """String parser.

        Returns:
            String: a token node that represeting a literal string
        """

        token = self.current_token
        self.consume_token(TokenType.STRING_CONST)
        node = String(token)
        return node

    def bool_false_parser(self) -> Boolean:
        """Boolean parser for the literal FALSE.

        Returns:
            Boolean: a token node that represeting a FALSE boolean type
        """

        token = self.current_token
        self.consume_token(TokenType.FALSE)
        node = Boolean(token)
        return node

    def bool_true_parser(self) -> Boolean:
        """Boolean parser for the literal TRUE.

        Returns:
            Boolean: a token node that represeting a TRUE boolean type
        """

        token = self.current_token
        self.consume_token(TokenType.TRUE)
        node = Boolean(token)
        return node

    def parse(self) -> Program:
        """Start the parser.

        Returns:
            Program: the entire tree structure originating from the analyzed source code
        """
        node = self.program()

        if self.current_token.type != TokenType.EOF:
            ParserErrorHandler.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN, token=self.current_token
            )

        return node
