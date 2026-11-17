import argparse
from pathlib import Path

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ast_printer import print_ast


DEFAULT_SOURCE = r"""
int age = 20;
int total = 0;
int i = 0;

if (age >= 18 && age < 60) {
    total = age + 5;
} else {
    total = 0;
}

while (i < 3) {
    total += i;
    i++;
}

for (int j = 0; j < 5; j++) {
    total += j;
}

do {
    i--;
} while (i > 0);
"""


def main():
    argument_parser = argparse.ArgumentParser(
        description="Mini C Compiler - lexical, syntax, AST and semantic analysis"
    )
    argument_parser.add_argument(
        "source_file",
        nargs="?",
        help="Optional path to a C source file. If omitted, the built-in demo runs.",
    )
    argument_parser.add_argument(
        "--tokens",
        action="store_true",
        help="Print tokens produced by lexical analysis.",
    )
    argument_parser.add_argument(
        "--ast",
        action="store_true",
        help="Print the Abstract Syntax Tree.",
    )
    args = argument_parser.parse_args()

    if args.source_file:
        source_path = Path(args.source_file)
        if not source_path.exists():
            print(f"Error: file not found: {source_path}")
            return 1
        source_code = source_path.read_text(encoding="utf-8")
    else:
        source_code = DEFAULT_SOURCE

    print("=" * 58)
    print("                 MINI C COMPILER")
    print("=" * 58)

    # Phase 1: Lexical analysis
    lexer = Lexer(source_code)
    tokens, lexical_errors = lexer.tokenize()

    print("\n[1] LEXICAL ANALYSIS")
    print(f"Tokens generated: {len(tokens)}")

    if args.tokens:
        for token in tokens:
            print(token)

    if lexical_errors:
        print("\nLexical errors:")
        for error in lexical_errors:
            print(error)

    # Phase 2: Syntax analysis and AST generation
    parser = Parser(tokens)
    program = parser.parse_program()

    print("\n[2] SYNTAX ANALYSIS")
    if parser.errors:
        for error in parser.errors:
            print(error)
    else:
        print("No syntax errors found.")

    # Phase 3: Semantic analysis
    print("\n[3] SEMANTIC ANALYSIS")
    semantic_analyzer = SemanticAnalyzer()
    semantic_errors = semantic_analyzer.analyze(program)

    if semantic_errors:
        for error in semantic_errors:
            print(error)
    else:
        print("No semantic errors found.")

    # Phase 4: AST
    if args.ast or not args.source_file:
        print("\n[4] ABSTRACT SYNTAX TREE")
        print_ast(program)

    print("\n" + "=" * 58)
    if lexical_errors or parser.errors or semantic_errors:
        print("COMPILATION COMPLETED WITH ERRORS")
        return 1

    print("COMPILATION SUCCESSFUL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
