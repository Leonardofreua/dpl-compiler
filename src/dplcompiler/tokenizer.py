# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                            Tokenizer (Lexical Analyzer)                                 #
#                                                                                         #
# This is where the source code will be broken and transformed into atoms (Tokens). It's  #
# also where some other Lexical Analyzer responsabilities will be performed, which are    #
# listed below:                                                                           #
#                                                                                         #
#       => Skip whitespaces;                                                              #
#       => Skip comments;                                                                 #
#       => Identify the set of Reserved Keywords;                                         #
#       => Handle lexical errors when a token is not found;                               #
#       => Count lines and columns when reading tokens.                                   #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                         #
#   Author: Leonardo Freua                                                                #
#                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from typing import Optional, List

from token import Token
from token_type import TokenType

from exceptions import TokenizerErrorHandler


def _get_reserved_keywords() -> dict:
    """Create a dictionary of reserved keywords.

    Returns:
        dict: a dictionary with all reserved keywords.
    """

    token_type_list = list(TokenType)
    start_index = token_type_list.index(TokenType.PROGRAM)
    end_index = token_type_list.index(TokenType.END)

    reserved_keywords = {
        token_type.value: token_type
        for token_type in token_type_list[start_index : end_index + 1]
    }
    return reserved_keywords


def _get_single_characters() -> List[str]:
    """Create a list of all supported special characters.

    Returns:
        List[str]: list containing all special characters
    """

    token_type_list = list(TokenType)
    start_index = token_type_list.index(TokenType.PLUS)
    end_index = token_type_list.index(TokenType.RBRACE)

    singles_characters = [
        toke_type.value for toke_type in token_type_list[start_index : end_index + 1]
    ]

    return singles_characters


class Tokenizer:
    """Tokenizer (Lexical Analyzer)

    Args:
        source_code (str): The source code that will be compiled.
    """

    RESERVED_KEYWORDS = _get_reserved_keywords()
    SINGLE_CHARACTERS = _get_single_characters()

    def __init__(self, source_code: str) -> None:
        self.source_code = source_code  # Source code
        self.pos = 0  # self.pos is an index into self.source_code
        self.current_token = None
        self.current_char = self.source_code[self.pos]  # The lexeme
        # Token line and column number
        self.t_line = 1
        self.t_column = 1

    def advance(self) -> None:
        """Advance the 'pos' pointer and set the 'current_char' variable"""

        if self.current_char == "\n":
            self.t_line += 1
            self.t_column = 0

        self.pos += 1
        if self.pos > len(self.source_code) - 1:
            self.current_char = None  # Indicates end of code
        else:
            self.current_char = self.source_code[self.pos]
            self.t_column += 1

    def tokenize_assign_statements(self) -> Optional[str]:
        """Tokenize the assignment statements returning the
        next character from the source_code buffer without incrementing
        the self.pos variable.

        Returns:
            Optional[str]: Token that represents an assignment statement.
        """

        tokenize_pos = self.pos + 1
        if tokenize_pos > len(self.source_code) - 1:
            return None
        else:
            return self.source_code[tokenize_pos]

    def handle_with_id_tokens(self) -> Token:
        """Handle identifiers and reserved keyboards.

        Returns:
            Token: the tokens representing a reserved keyword
        """

        token = Token(type=None, value=None, line=self.t_line, column=self.t_column)

        value = ""
        while (
            self.current_char is not None
            and self.current_char.isalnum()
            or self.current_char == TokenType.UNDER_SCORE.value
        ):
            value += self.current_char
            self.advance()

        token_type = self.RESERVED_KEYWORDS.get(value.upper())
        if token_type is None:
            token.type = TokenType.ID
            token.value = value
        else:
            token.type = token_type
            token.value = value.upper()

        return token

    def skip_whitespace(self) -> None:
        """Skip whitespaces in the code"""

        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self) -> None:
        """Skip code comments"""

        while self.current_char != "}":
            self.advance()
        self.advance()

    def number(self) -> Token:
        """Return a (multidigit) integer or float consumed from the input.

        Returns:
            Token: a token represeting a number in an expression
        """

        token = Token(type=None, value=None, line=self.t_line, column=self.t_column)

        value = ""
        while self.current_char is not None and self.current_char.isdigit():
            value += self.current_char
            self.advance()

        if self.current_char == ".":
            value += self.current_char
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                value += self.current_char
                self.advance()

            token.type = TokenType.REAL_CONST
            token.value = float(value)
        else:
            token.type = TokenType.INTEGER_CONST
            token.value = int(value)

        return token

    def string(self) -> Token:
        """Return a literal string token (STRING_CONST).

        Returns:
            Token: a token representing a literal string.
        """

        token = Token(type=None, value=None, line=self.t_line, column=self.t_column)

        self.advance()

        value = ""
        while (
            self.current_char is not None
            and self.current_char.isalpha()
            or self.current_char in self.SINGLE_CHARACTERS
        ):
            value += self.current_char
            self.advance()

            if self.current_char.isspace():
                value += " "
                self.skip_whitespace()

        self.advance()

        token.type = TokenType.STRING_CONST
        token.value = value

        return token

    def get_next_token(self) -> Token:
        """Here the Lexical Analysis will take place, so the sentences will be broken
        one at a time into smaller parts

        Returns:
            Token: the Token object with all informations about the found token

        Raises:
            ValueError: a TokenizeError when the current_token is not found in the grammar
        """

        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == "{":
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isalpha():
                return self.handle_with_id_tokens()

            if self.current_char in ["'", '"']:
                return self.string()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == ":" and self.tokenize_assign_statements() == "=":
                token = Token(
                    type=TokenType.ASSIGN,
                    value=TokenType.ASSIGN.value,
                    line=self.t_line,
                    column=self.t_column,
                )
                self.advance()
                self.advance()
                return token

            try:
                token_type = TokenType(self.current_char)
            except ValueError:
                TokenizerErrorHandler.error(
                    self.current_char, self.t_line, self.t_column
                )
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,
                    line=self.t_line,
                    column=self.t_column,
                )
                self.advance()
                return token

        return Token(type=TokenType.EOF, value=None)
