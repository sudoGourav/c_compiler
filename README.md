# Mini C Compiler

A small educational C-subset compiler written in Python. It runs locally from the terminal and currently includes:

1. Lexical analysis (tokenization)
2. Syntax analysis (recursive-descent parser)
3. Abstract Syntax Tree (AST) generation and printing
4. Basic semantic analysis and symbol-table checks

## Requirements

- Python 3.9 or newer
- No third-party Python packages are required

## Run

From the project root:

```bash
python main.py
```

Run a C source file:

```bash
python main.py sample.c
```

Print tokens:

```bash
python main.py sample.c --tokens
```

Print the AST:

```bash
python main.py sample.c --ast
```

## Project structure

```text
mini-c-compiler/
├── compiler/
│   ├── __init__.py
│   ├── tokens.py
│   ├── errors.py
│   ├── lexer.py
│   ├── parser.py
│   ├── ast_nodes.py
│   ├── ast_printer.py
│   └── semantic.py
├── main.py
├── sample.c
└── README.md
```

## Supported language subset

- Basic data types: `int`, `float`, `double`, `char`
- Variable declarations and initialization
- Identifiers and numeric/character/string literals
- Arithmetic operators: `+`, `-`, `*`, `/`, `%`
- Relational and logical operators
- Assignment and compound assignment
- Prefix/postfix increment and decrement
- `if`, `else`, `while`, `for`, `do-while`
- Blocks and `return`
- Single-line and multi-line comments

## Current limitations

This is not a complete implementation of the C standard. Function declarations/calls, arrays, pointers, structs, preprocessor expansion, switch statements, and machine-code generation are not implemented. The semantic analyzer performs basic symbol and type checks; it is not a full C type system.

The project currently analyzes source code and produces an AST. It does not execute C programs or generate native machine code.
