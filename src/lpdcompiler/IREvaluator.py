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

    def evaluate(self, optimize, llvmdump):
        self.codegen.visit(self.tree)

        if llvmdump:
            print("\n======== Unoptimized LLVM IR\n")
            print(str(self.codegen.module))

        # Convert LLVM IR into in-memory representation
        llvmmod = llvm.parse_assembly(str(self.codegen.module))

        # Optimize the module
        if optimize:
            pass_mger_builder = llvm.create_pass_manager_builder()
            pass_mger_builder.opt_level = 2
            module_pass_mger = llvm.create_module_pass_manager()
            pass_mger_builder.populate(module_pass_mger)
            module_pass_mger.run(llvmmod)

            if llvmdump:
                print("\n======== Optimized LLVM IR\n")
                print(str(llvmmod))

        target_machine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvmmod, target_machine) as mcjit_c:
            mcjit_c.finalize_object()

            if llvmdump:
                print("\n======== Machine code\n")
                print(target_machine.emit_assembly(llvmmod))

            fptr = CFUNCTYPE(c_double)(
                mcjit_c.get_function_address(self.codegen.func_name))

            result = fptr()
            return result
