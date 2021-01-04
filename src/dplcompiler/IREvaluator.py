import os
import llvmlite.binding as llvm
from typing import Any
from ctypes import CFUNCTYPE, c_double

from CodeGenerator import CodeGenerator
from AST import Program
from symbols import SymbolTable


class IREvaluator:
    def __init__(
        self, tree: Program, symbol_table: SymbolTable, source_file: str
    ) -> None:
        llvm.initialize()
        llvm.initialize_all_targets()
        llvm.initialize_all_asmprinters()

        self.tree = tree
        self.codegen = CodeGenerator(symbol_table)
        self.source_file = source_file
        self.target = llvm.Target.from_triple(llvm.get_default_triple())

    def _save_code(self, source_module: str, file_name: str, extension: str) -> None:
        """Saves the generated code.

        Args:
            source_module (str): source code that will be saved
            file_name (str): file name of the generated code
            extension (str): extension file
        """

        dist_dir = f"{os.getcwd()}/dist"

        if not os.path.exists(dist_dir):
            os.mkdir(dist_dir)

        with open(f"{os.path.join(dist_dir, file_name)}.{extension}", "w") as code:
            code.write(source_module)

    def _optimize_module(self, optimize: bool, llvmdump: bool, source_module) -> None:
        """performs intermediate code level 2 optimization.

        Args:
            optimize (bool): flag to indicate the optimization
            llvmdump (bool): flag to indicate the impression of the results achieved
            source_module: the source module that will be optimized
        """

        if optimize:
            pass_mger_builder = llvm.create_pass_manager_builder()
            pass_mger_builder.opt_level = 2
            module_pass_mger = llvm.create_module_pass_manager()
            pass_mger_builder.populate(module_pass_mger)
            module_pass_mger.run(source_module)

            str_source_module = str(source_module)
            self._save_code(str_source_module, "_optz_ir_dpl", "ll")

            if llvmdump:
                print("\n======== Optimized LLVM IR ========\n")
                print(str_source_module)

    def evaluate(self, optimize: bool, llvmdump: bool) -> Any:
        """Validates the AST already transformed into LLVM IR, calls the responsible
        method to optimize the code and turns it into Machine code.

        Args:
            optimize (bool): flag to indicate the optimization
            llvmdump (bool): flag to indicate the impression of the results achieved
            by the LLVM
        """

        self.codegen.visit(self.tree)
        self.codegen.module.triple = self.target.triple
        self.codegen.module.name = self.source_file

        str_source_module = str(self.codegen.module)

        if llvmdump:
            print("\n======== Unoptimized LLVM IR ========\n")
            print(str_source_module)

        self._save_code(str_source_module, "unoptz_ir_dpl", "ll")

        # Convert LLVM IR into in-memory representation
        llvmmod = llvm.parse_assembly(str(self.codegen.module))

        # Optimize the module
        self._optimize_module(optimize, llvmdump, llvmmod)

        cpu = llvm.get_host_cpu_name()
        target_machine = self.target.create_target_machine(cpu)
        with llvm.create_mcjit_compiler(llvmmod, target_machine) as mcjit_c:
            mcjit_c.finalize_object()

            asm_code = target_machine.emit_assembly(llvmmod)

            if llvmdump:
                print("\n======== Machine code ========\n")
                print(asm_code)

            self._save_code(asm_code, "asm_dpl", "asm")

            fptr = CFUNCTYPE(c_double)(
                mcjit_c.get_function_address(self.codegen.func_name)
            )

            result = fptr()
            return result
