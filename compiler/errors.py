from dataclasses import dataclass


@dataclass
class CompilerError:
    error_type: str
    message: str
    line: int
    column: int

    def to_dict(self):
        return {
            "type": self.error_type,
            "message": self.message,
            "line": self.line,
            "column": self.column,
        }

    def __str__(self):
        return (
            f"{self.error_type} at Line {self.line}, "
            f"Column {self.column}: {self.message}"
        )
