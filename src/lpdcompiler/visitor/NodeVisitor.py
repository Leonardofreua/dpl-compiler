# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                               Node Visitor (Visitor Pattern)                          #
#                                                                                       #
# The Visitor Pattern triggered by the classes Handler.py and SymbolTableHandler.py,    #
# works with the objective of orchestrating the method calls according to the object    #
# being requested, however, without being directly coupled to the one being executed.   #
#                                                                                       #
# Reference: https://pt.wikipedia.org/wiki/Visitor_Pattern                              #
#                                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                       #
#   Author: Leonardo Freua                                                              #
#                                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class NodeVisitor:
    def visit(self, node):
        """Visit each node of the tree and executes the corresponding method.

        Args:
            node: a node represented by an object defined in class AST. 
                Examples: - Program
                          - Block
                          - VarDeclaration
                          - Type
                          - BinaryOperator
                          - UnaryOperator
                          - Num
                          - Compound
                          - ...

        Returns:
            method: a method correspoding a node type.
                Examples: - visit_Program()
                          - visit_Block()
                          - visit_VarDeclaration()
                          - visit_Type()
                          - visit_BinaryOperator()
                          - visit_UnaryOperator()
                          - visit_Num()
                          - visit_Compound()
                          - visit_...
        """
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Raise a exception when the node is not found.

        Args:
            node: node not found

        Raises:
            Exception: Shows a message with the node that was not found
        """
        raise Exception(f"No visit_{type(node).__name__} method")
