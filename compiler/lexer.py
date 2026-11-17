from compiler.tokens import Token
from compiler.errors import CompilerError


class Lexer:
    KEYWORDS = {
        "int", "float", "double", "char", "void",
        "if", "else", "while", "for", "do", "return",
        "break", "continue", "const", "long", "short",
        "unsigned", "signed", "switch", "case", "default",
    }

    TWO_CHAR_OPERATORS = {
        "==", "!=", "<=", ">=", "++", "--",
        "+=", "-=", "*=", "/=", "%=", "&&", "||",
        "<<", ">>", "->",
    }

    ONE_CHAR_TOKENS = set(
        "+-*/%=<>!&|^~?:;,.()[]{}#"
    )

    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.errors = []
        self.position = 0
        self.line = 1
        self.column = 1

    def current(self, offset=0):
        index = self.position + offset
        if index >= len(self.source):
            return None
        return self.source[index]

    def advance(self):
        char = self.current()
        if char is None:
            return None

        self.position += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def add_token(self, token_type, value, line, column):
        self.tokens.append(Token(token_type, value, line, column))

    def add_error(self, message, line=None, column=None):
        self.errors.append(
            CompilerError(
                "Lexical Error",
                message,
                line if line is not None else self.line,
                column if column is not None else self.column,
            )
        )

    def tokenize(self):
        while self.current() is not None:
            char = self.current()

            if char.isspace():
                self.advance()
                continue

            start_line = self.line
            start_column = self.column

            # Single-line comment
            if char == "/" and self.current(1) == "/":
                while self.current() is not None and self.current() != "\n":
                    self.advance()
                continue

            # Multi-line comment
            if char == "/" and self.current(1) == "*":
                self.advance()
                self.advance()
                closed = False

                while self.current() is not None:
                    if self.current() == "*" and self.current(1) == "/":
                        self.advance()
                        self.advance()
                        closed = True
                        break
                    self.advance()

                if not closed:
                    self.add_error(
                        "Unterminated multi-line comment",
                        start_line,
                        start_column,
                    )
                continue

            # Identifier or keyword
            if char.isalpha() or char == "_":
                value = ""
                while (
                    self.current() is not None
                    and (self.current().isalnum() or self.current() == "_")
                ):
                    value += self.advance()

                token_type = "KEYWORD" if value in self.KEYWORDS else "IDENTIFIER"
                self.add_token(token_type, value, start_line, start_column)
                continue

            # Integer or decimal floating-point literal
            if char.isdigit():
                value = ""
                while self.current() is not None and self.current().isdigit():
                    value += self.advance()

                token_type = "INTEGER_LITERAL"

                if self.current() == "." and (
                    self.current(1) is not None
                    and self.current(1).isdigit()
                ):
                    value += self.advance()
                    while self.current() is not None and self.current().isdigit():
                        value += self.advance()
                    token_type = "FLOAT_LITERAL"

                self.add_token(token_type, value, start_line, start_column)
                continue

            # String and character literals
            if char in ('"', "'"):
                quote = self.advance()
                value = quote
                closed = False

                while self.current() is not None:
                    current_char = self.advance()
                    value += current_char

                    if current_char == "\\" and self.current() is not None:
                        value += self.advance()
                        continue

                    if current_char == quote:
                        closed = True
                        break

                    if current_char == "\n":
                        break

                if not closed:
                    literal_name = "string" if quote == '"' else "character"
                    self.add_error(
                        f"Unterminated {literal_name} literal",
                        start_line,
                        start_column,
                    )
                    continue

                token_type = "STRING_LITERAL" if quote == '"' else "CHAR_LITERAL"
                self.add_token(token_type, value, start_line, start_column)
                continue

            # Multi-character operators
            two_chars = (char or "") + (self.current(1) or "")
            if two_chars in self.TWO_CHAR_OPERATORS:
                self.advance()
                self.advance()
                self.add_token("OPERATOR", two_chars, start_line, start_column)
                continue

            # Single-character tokens
            if char in self.ONE_CHAR_TOKENS:
                self.advance()

                if char in ";,(){}[]":
                    token_type = "PUNCTUATION"
                elif char == "#":
                    token_type = "PREPROCESSOR"
                else:
                    token_type = "OPERATOR"

                self.add_token(token_type, char, start_line, start_column)
                continue

            self.add_error(
                f"Unrecognized character '{char}'",
                start_line,
                start_column,
            )
            self.advance()

        return self.tokens, self.errors
