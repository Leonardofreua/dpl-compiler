# DPL Compiler

This compiler aims to demonstrate the construction of programming lannguage from scratch. The base language used is **Pascal**.

# Compiler Features

* Lexer;
* Parser;
* Symbol Table;
* Semantic Analysis;
* Intermediate code Generation (IR) using LLVM;

# Language Features

* Primitive types: ``Bool, Real, Integer and String``;
* Arithmetic Operations (Binary and Unary);
* Command to print results on the screen (Writeln);

# Installation

Run ``pip install -r requirements.txt`` to install the **[llvmlite](https://github.com/numba/llvmlite)** dependecy;

# Usage

Go to the ``src/dplcompiler`` directory and Run ``python3 app.py <source_file.dpl>`` (There is an example in ``src/dplcompiler/dpl_source_code/``)
