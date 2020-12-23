# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                    Symbol Table                                           #
#                                                                                           #
# In this class, the structure of the Symbol Table is configured, as well as its actions    #
# of adding and searching for symbols, token listing and initialization of primitive types  #                                                                       #
#                                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                           #
#   Author: Leonardo Freua                                                                  #
#                                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union, Optional, Any
from collections import OrderedDict

from .Symbols import BuiltinTypeSymbol, VarSymbol


class SymbolTable:
    def __init__(self) -> None:
        self._symbols = OrderedDict()
        self.__init_builtins()

    def __str__(self) -> str:
        """Displays the complete symbol table.

        Returns:
            str: the symbol the table formatted
        """

        return self._format_symbol_table_content("Symbol table", self._symbols.items())

    __repr__ = __str__

    def list_tokens(self) -> str:
        """Displays the complete list of tokens.

        Returns:
            str: the list of tokens formatted
        """

        return self._format_symbol_table_content("Tokens", self._symbols.keys())

    def __init_builtins(self) -> None:
        """Initialize the primitive types."""

        self.add_token(BuiltinTypeSymbol("INTEGER"))
        self.add_token(BuiltinTypeSymbol("REAL"))
        self.add_token(BuiltinTypeSymbol("STRING"))
        self.add_token(BuiltinTypeSymbol("BOOLEAN"))

    def add_token(self, symbol):  # type: (Union[BuiltinTypeSymbol, VarSymbol])-> None
        """Add a new symbol in the table.

        Args:
            symbol (Union[BuiltinTypeSymbol, VarSymbol]): symbol that will be add
        """

        self._symbols[symbol.name] = symbol

    def get_token(self, name: str) -> Optional[BuiltinTypeSymbol]:
        """Get a symbol in the table by name.

        Args:
            name (str): name of the symbol

        Returns:
            Optional[BuiltinTypeSymbol]: a found symbol
        """

        symbol = self._symbols.get(name)
        return symbol

    def _format_symbol_table_content(self, title: str, symbols: Any) -> str:
        """Format the symbol table content.

        Args:
            title (str): title of the content that will be displayed
            symbols (Any): symbol table items or keys

        Returns:
            str: formatted content
        """

        header = f"\t\t:::: {title} ::::"
        lines = ["\n", header, "__" * len(header)]
        if type(symbols).__name__ == "odict_items":
            lines.extend((f"| {key}: {value}") for key, value in self._symbols.items())
        elif type(symbols).__name__ == "odict_keys":
            lines.extend((f"| {key}") for key in self._symbols.keys())

        lines.append("\n")
        formatted_content = "\n".join(lines)
        return formatted_content
