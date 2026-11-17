from dataclasses import dataclass
from compiler.errors import CompilerError
from compiler.ast_nodes import (
    Program, Declaration, Assignment, BinaryExpression, UnaryExpression,
    Number, Identifier, Literal, Condition, LogicalExpression,
    IfStatement, WhileStatement, ForStatement, DoWhileStatement,
    Block, ReturnStatement,
)


@dataclass
class Symbol:
    name: str
    data_type: str
    line: int = 0


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, data_type):
        current_scope = self.scopes[-1]
        if name in current_scope:
            return False
        current_scope[name] = Symbol(name, data_type)
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class SemanticAnalyzer:
    NUMERIC_TYPES = {"int", "float", "double", "long", "short", "unsigned", "signed"}

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def add_error(self, message, line=0, column=0):
        self.errors.append(
            CompilerError("Semantic Error", message, line or 1, column or 1)
        )

    def analyze(self, program):
        self.visit(program)
        return self.errors

    def visit(self, node):
        if node is None:
            return

        if isinstance(node, Program):
            for statement in node.statements:
                self.visit(statement)

        elif isinstance(node, Block):
            self.symbol_table.enter_scope()
            for statement in node.statements:
                self.visit(statement)
            self.symbol_table.exit_scope()

        elif isinstance(node, Declaration):
            if not self.symbol_table.declare(node.name, node.data_type):
                self.add_error(
                    f"Variable '{node.name}' is already declared in this scope"
                )
            if node.value is not None:
                value_type = self.infer_type(node.value)
                if not self.compatible(node.data_type, value_type):
                    self.add_error(
                        f"Cannot assign value of type '{value_type}' "
                        f"to variable '{node.name}' of type '{node.data_type}'"
                    )

        elif isinstance(node, Assignment):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                self.add_error(f"Variable '{node.name}' is not declared")
            if node.operator in {"++", "--", "pre++", "pre--"}:
                if symbol and symbol.data_type not in self.NUMERIC_TYPES:
                    self.add_error(
                        f"Operator '{node.operator}' requires a numeric variable"
                    )
            elif node.value is not None:
                value_type = self.infer_type(node.value)
                if symbol and not self.compatible(symbol.data_type, value_type):
                    self.add_error(
                        f"Cannot assign value of type '{value_type}' "
                        f"to variable '{node.name}' of type '{symbol.data_type}'"
                    )

        elif isinstance(node, IfStatement):
            self.infer_type(node.condition)
            self.visit(node.then_branch)
            self.visit(node.else_branch)

        elif isinstance(node, WhileStatement):
            self.infer_type(node.condition)
            self.visit(node.body)

        elif isinstance(node, ForStatement):
            self.symbol_table.enter_scope()
            self.visit(node.initialization)
            if node.condition is not None:
                self.infer_type(node.condition)
            if node.update is not None:
                self.visit(node.update)
            self.visit(node.body)
            self.symbol_table.exit_scope()

        elif isinstance(node, DoWhileStatement):
            self.visit(node.body)
            self.infer_type(node.condition)

        elif isinstance(node, ReturnStatement):
            if node.value is not None:
                self.infer_type(node.value)

    def compatible(self, target, source):
        if source == "unknown":
            return True
        if target == source:
            return True
        if target in self.NUMERIC_TYPES and source in self.NUMERIC_TYPES:
            return True
        return False

    def infer_type(self, node):
        if node is None:
            return "unknown"

        if isinstance(node, Number):
            return "float" if "." in node.value else "int"

        if isinstance(node, Literal):
            return node.literal_type

        if isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                self.add_error(f"Variable '{node.name}' is not declared")
                return "unknown"
            return symbol.data_type

        if isinstance(node, UnaryExpression):
            operand_type = self.infer_type(node.operand)
            if node.operator in {"+", "-"} and operand_type not in self.NUMERIC_TYPES:
                self.add_error(
                    f"Unary operator '{node.operator}' requires a numeric operand"
                )
            return operand_type

        if isinstance(node, BinaryExpression):
            left_type = self.infer_type(node.left)
            right_type = self.infer_type(node.right)
            if left_type not in self.NUMERIC_TYPES or right_type not in self.NUMERIC_TYPES:
                self.add_error(
                    f"Operator '{node.operator}' requires numeric operands"
                )
                return "unknown"
            if "double" in {left_type, right_type}:
                return "double"
            if "float" in {left_type, right_type}:
                return "float"
            return "int"

        if isinstance(node, Condition):
            self.infer_type(node.left)
            self.infer_type(node.right)
            return "bool"

        if isinstance(node, LogicalExpression):
            self.infer_type(node.left)
            self.infer_type(node.right)
            return "bool"

        if isinstance(node, Assignment):
            self.visit(node)
            symbol = self.symbol_table.lookup(node.name)
            return symbol.data_type if symbol else "unknown"

        return "unknown"
