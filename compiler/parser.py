from compiler.errors import CompilerError
from compiler.ast_nodes import (
    Program, Declaration, Assignment, BinaryExpression, UnaryExpression,
    Number, Identifier, Literal, Condition, LogicalExpression,
    IfStatement, WhileStatement, ForStatement, DoWhileStatement,
    Block, ReturnStatement, ExpressionStatement,
)


class Parser:
    DATA_TYPES = {
        "int", "float", "double", "char", "void",
        "long", "short", "unsigned", "signed",
    }

    ASSIGNMENT_OPERATORS = {"=", "+=", "-=", "*=", "/=", "%="}
    RELATIONAL_OPERATORS = {"==", "!=", "<", ">", "<=", ">="}

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def current(self, offset=0):
        index = self.position + offset
        return self.tokens[index] if index < len(self.tokens) else None

    def advance(self):
        token = self.current()
        if token is not None:
            self.position += 1
        return token

    def check(self, value):
        token = self.current()
        return token is not None and token.value == value

    def check_type(self, token_type):
        token = self.current()
        return token is not None and token.type == token_type

    def add_error(self, message):
        token = self.current()
        if token is not None:
            line, column = token.line, token.column
        elif self.tokens:
            last = self.tokens[-1]
            line, column = last.line, last.column + len(last.value)
        else:
            line, column = 1, 1

        self.errors.append(
            CompilerError("Syntax Error", message, line, column)
        )

    def expect(self, value, message=None):
        if self.check(value):
            return self.advance()
        self.add_error(message or f"Expected '{value}'")
        return None

    # ---------- Expressions: precedence from low to high ----------

    def parse_expression(self):
        return self.parse_assignment_expression()

    def parse_assignment_expression(self):
        left = self.parse_logical_or()
        if left is None:
            return None

        if self.current() is not None and self.current().value in self.ASSIGNMENT_OPERATORS:
            operator = self.advance().value
            right = self.parse_assignment_expression()
            if right is None:
                return None
            if isinstance(left, Identifier):
                return Assignment(left.name, operator, right)
            self.add_error("Left side of assignment must be a variable")
            return None

        return left

    def parse_logical_or(self):
        left = self.parse_logical_and()
        if left is None:
            return None
        while self.check("||"):
            operator = self.advance().value
            right = self.parse_logical_and()
            if right is None:
                return None
            left = LogicalExpression(left, operator, right)
        return left

    def parse_logical_and(self):
        left = self.parse_equality()
        if left is None:
            return None
        while self.check("&&"):
            operator = self.advance().value
            right = self.parse_equality()
            if right is None:
                return None
            left = LogicalExpression(left, operator, right)
        return left

    def parse_equality(self):
        left = self.parse_relational()
        if left is None:
            return None
        while self.check("==") or self.check("!="):
            operator = self.advance().value
            right = self.parse_relational()
            if right is None:
                return None
            left = Condition(left, operator, right)
        return left

    def parse_relational(self):
        left = self.parse_additive()
        if left is None:
            return None
        while (
            self.current() is not None
            and self.current().value in {"<", ">", "<=", ">="}
        ):
            operator = self.advance().value
            right = self.parse_additive()
            if right is None:
                return None
            left = Condition(left, operator, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        if left is None:
            return None
        while self.check("+") or self.check("-"):
            operator = self.advance().value
            right = self.parse_multiplicative()
            if right is None:
                return None
            left = BinaryExpression(left, operator, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        if left is None:
            return None
        while (
            self.check("*") or self.check("/") or self.check("%")
        ):
            operator = self.advance().value
            right = self.parse_unary()
            if right is None:
                return None
            left = BinaryExpression(left, operator, right)
        return left

    def parse_unary(self):
        if self.check("+") or self.check("-") or self.check("!"):
            operator = self.advance().value
            operand = self.parse_unary()
            if operand is None:
                return None
            return UnaryExpression(operator, operand)

        if self.check("++") or self.check("--"):
            operator = self.advance().value
            operand = self.parse_unary()
            if not isinstance(operand, Identifier):
                self.add_error("Increment/decrement requires a variable")
                return None
            return Assignment(operand.name, "pre" + operator, operand)

        return self.parse_postfix()

    def parse_postfix(self):
        expression = self.parse_primary()
        if expression is None:
            return None

        if self.check("++") or self.check("--"):
            operator = self.advance().value
            if not isinstance(expression, Identifier):
                self.add_error("Increment/decrement requires a variable")
                return None
            return Assignment(expression.name, operator, expression)

        return expression

    def parse_primary(self):
        token = self.current()
        if token is None:
            self.add_error("Expected an expression")
            return None

        if token.type in {"INTEGER_LITERAL", "FLOAT_LITERAL"}:
            self.advance()
            return Number(token.value)

        if token.type == "CHAR_LITERAL":
            self.advance()
            return Literal(token.value, "char")

        if token.type == "STRING_LITERAL":
            self.advance()
            return Literal(token.value, "string")

        if token.type == "IDENTIFIER":
            self.advance()
            return Identifier(token.value)

        if self.check("("):
            self.advance()
            expression = self.parse_expression()
            if expression is None:
                return None
            if not self.expect(")", "Expected ')' after expression"):
                return None
            return expression

        self.add_error(f"Unexpected token '{token.value}' in expression")
        return None

    # ---------- Statements ----------

    def parse_declaration(self, consume_semicolon=True):
        data_type_token = self.advance()
        if not self.check_type("IDENTIFIER"):
            self.add_error("Expected variable name after data type")
            return None

        name = self.advance().value
        value = None

        if self.check("="):
            self.advance()
            value = self.parse_expression()
            if value is None:
                return None

        declaration = Declaration(data_type_token.value, name, value)

        if consume_semicolon and not self.expect(
            ";", "Expected ';' after variable declaration"
        ):
            return None

        return declaration

    def parse_assignment_statement(self, consume_semicolon=True):
        expression = self.parse_expression()
        if expression is None:
            return None

        if not isinstance(expression, Assignment):
            self.add_error("Expected an assignment or increment/decrement")
            return None

        if consume_semicolon and not self.expect(
            ";", "Expected ';' after assignment"
        ):
            return None

        return expression

    def parse_condition(self):
        return self.parse_expression()

    def parse_if_statement(self):
        self.advance()
        if not self.expect("(", "Expected '(' after if"):
            return None

        condition = self.parse_condition()
        if condition is None:
            return None

        if not self.expect(")", "Expected ')' after if condition"):
            return None

        then_branch = self.parse_statement()
        if then_branch is None:
            return None

        else_branch = None
        if self.check("else"):
            self.advance()
            else_branch = self.parse_statement()
            if else_branch is None:
                return None

        return IfStatement(condition, then_branch, else_branch)

    def parse_while_statement(self):
        self.advance()
        if not self.expect("(", "Expected '(' after while"):
            return None

        condition = self.parse_condition()
        if condition is None:
            return None

        if not self.expect(")", "Expected ')' after while condition"):
            return None

        body = self.parse_statement()
        if body is None:
            return None

        return WhileStatement(condition, body)

    def parse_for_statement(self):
        self.advance()
        if not self.expect("(", "Expected '(' after for"):
            return None

        initialization = None
        condition = None
        update = None

        if not self.check(";"):
            if (
                self.check_type("KEYWORD")
                and self.current().value in self.DATA_TYPES
            ):
                initialization = self.parse_declaration(consume_semicolon=False)
            else:
                initialization = self.parse_expression()

            if initialization is None:
                return None

        if not self.expect(";", "Expected ';' after for-loop initialization"):
            return None

        if not self.check(";"):
            condition = self.parse_condition()
            if condition is None:
                return None

        if not self.expect(";", "Expected ';' after for-loop condition"):
            return None

        if not self.check(")"):
            update = self.parse_expression()
            if update is None:
                return None

        if not self.expect(")", "Expected ')' after for-loop update"):
            return None

        body = self.parse_statement()
        if body is None:
            return None

        return ForStatement(initialization, condition, update, body)

    def parse_do_while_statement(self):
        self.advance()

        body = self.parse_statement()
        if body is None:
            return None

        if not self.expect("while", "Expected 'while' after do block"):
            return None

        if not self.expect("(", "Expected '(' after while"):
            return None

        condition = self.parse_condition()
        if condition is None:
            return None

        if not self.expect(")", "Expected ')' after do-while condition"):
            return None

        if not self.expect(";", "Expected ';' after do-while statement"):
            return None

        return DoWhileStatement(body, condition)

    def parse_return_statement(self):
        self.advance()
        value = None
        if not self.check(";"):
            value = self.parse_expression()
            if value is None:
                return None
        if not self.expect(";", "Expected ';' after return statement"):
            return None
        return ReturnStatement(value)

    def parse_block(self):
        if not self.expect("{", "Expected '{' to start block"):
            return None

        statements = []
        while self.current() is not None and not self.check("}"):
            old_position = self.position
            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)
            else:
                self.synchronize()

            if self.position == old_position:
                self.advance()

        if not self.expect("}", "Expected '}' to close block"):
            return None

        return Block(statements)

    def parse_statement(self):
        token = self.current()
        if token is None:
            return None

        if token.value == "{":
            return self.parse_block()

        if token.type == "KEYWORD" and token.value in self.DATA_TYPES:
            return self.parse_declaration()

        if token.value == "if":
            return self.parse_if_statement()

        if token.value == "while":
            return self.parse_while_statement()

        if token.value == "for":
            return self.parse_for_statement()

        if token.value == "do":
            return self.parse_do_while_statement()

        if token.value == "return":
            return self.parse_return_statement()

        if token.type == "IDENTIFIER":
            return self.parse_assignment_statement()

        self.add_error(f"Unexpected token '{token.value}'")
        return None

    # ---------- Program and error recovery ----------

    def parse_program(self):
        statements = []

        while self.current() is not None:
            old_position = self.position
            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)
            else:
                self.synchronize()

            if self.position == old_position:
                self.advance()

        return Program(statements)

    def synchronize(self):
        while self.current() is not None:
            if self.check(";"):
                self.advance()
                return

            if self.check("}"):
                return

            if (
                self.check_type("KEYWORD")
                and self.current().value in self.DATA_TYPES
            ):
                return

            if self.current().value in {"if", "while", "for", "do", "return"}:
                return

            self.advance()
