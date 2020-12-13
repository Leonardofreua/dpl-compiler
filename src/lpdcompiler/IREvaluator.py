import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_double

from CodeGenerator import CodeGenerator


class IREvaluator:
    def __init__(self, tree, symbol_table) -> None:
        llvm.initialize()
        llvm.initialize_all_targets()
        llvm.initialize_all_asmprinters()

        self.tree = tree
        self.codegen = CodeGenerator(symbol_table)
        self.target = llvm.Target.from_default_triple()

    def evaluate(self, optimize=True, llvmdump=False):
        self.codegen.visit(self.tree)

        if llvmdump:
            print("\n======== Unoptimized LLVM IR\n")
            print(str(self.codegen.module))

        # Convert LLVM IR into in-memory representation
        llvmmod = llvm.parse_assembly(str(self.codegen.module))

        # Optimize the module
        if optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 2
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvmmod)

            if llvmdump:
                print("\n======== Optimized LLVM IR\n")
                print(str(llvmmod))

        target_machine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvmmod, target_machine) as ee:
            ee.finalize_object()

            if llvmdump:
                print("\n======== Machine code\n")
                print(target_machine.emit_assembly(llvmmod))

            fptr = CFUNCTYPE(c_double)(ee.get_function_address(self.codegen.func_name))

            result = fptr()
            return result
