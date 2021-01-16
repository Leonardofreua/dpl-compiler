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

from tokenizer import Tokenizer
from parser import Parser
from handler import Handler
from semantic_handler import SemanticHandler
from IR_evaluator import IREvaluator

from exceptions.error import ParserError, TokenizeError, SemanticError


def set_cli():
    argparser = argparse.ArgumentParser(
        prog="DPL Compiler", description="DPL Compiler."
    )

    argparser.add_argument("sourcefile", help="DPL source file.")
    argparser.add_argument(
        "-sb", action="store_true", help="Display Symbol table content"
    )
    argparser.add_argument(
        "-lt", action="store_true", help="Display the list of tokens"
    )
    argparser.add_argument(
        "-optz", action="store_true", default=True, help="Optimize the LLVM IR code."
    )
    argparser.add_argument("-llvmd", action="store_true", help="Display LLVM results")
    args = argparser.parse_args()
    return args


def start():
    args = set_cli()

    sourcefile = args.sourcefile
    show_symtab = args.sb
    show_list_tokens = args.lt
    optimize_ir_code = args.optz
    show_llvm_result = args.llvmd
    source_code = open(sourcefile, "r").read()

    try:
        tokenizer = Tokenizer(source_code)
        parser = Parser(tokenizer)
        tree = parser.parse()
        semantic_handler = SemanticHandler()
        semantic_handler.visit(tree)

        if show_symtab:
            print(semantic_handler.symbol_table)

        if show_list_tokens:
            print(semantic_handler.symbol_table.list_tokens())

        handler = Handler(tree)
        handler.handle()
        evalutor = IREvaluator(tree, semantic_handler.symbol_table, sourcefile)
        evalutor.evaluate(optimize=optimize_ir_code, llvmdump=show_llvm_result)
    except (ParserError, TokenizeError, SemanticError) as err:
        print(err.message)
        sys.exit(1)


if __name__ == "__main__":
    start()
