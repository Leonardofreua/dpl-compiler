# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                Compiler Initializer                                   #
#                                                                                       #
# Here the CLI is configured to receive the file containing the source code and the     #
# Lexical Analyzer (Tokenizer), Parser (Syntactic) Symbol Table Handler and main        #
# Handler (responsible for using the visitor pattern to call the necessary methods to   #
# deal with the tokenized code) are initialized.                                        #
#                                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                       #
#   Author: Leonardo Freua                                                              #
#                                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import sys
import argparse

from Tokenizer import Tokenizer
from Parser import Parser
from Handler import Handler
from SemanticHandler import SemanticHandler

from exceptions.error import ParserError, TokenizeError, SemanticError


def set_cli():
    argparser = argparse.ArgumentParser(
        prog="LPD Compiler", description="LPD Compiler."
    )

    argparser.add_argument("sourcefile", help="LPD source file.")
    args = argparser.parse_args()

    return args


def start():
    args = set_cli()

    sourcefile = args.sourcefile
    source_code = open(sourcefile, "r").read()

    try:
        tokenizer = Tokenizer(source_code)
        parser = Parser(tokenizer)
        tree = parser.parse()
        semantic_handler = SemanticHandler()
        semantic_handler.visit(tree)

        print(semantic_handler.symbol_table.list_tokens())
        print(semantic_handler.symbol_table)
    except (ParserError, TokenizeError, SemanticError) as e:
        print(e.message)
        sys.exit(1)

    handler = Handler(tree)
    handler.handle()


if __name__ == "__main__":
    start()
