from dataclasses import dataclass


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def __repr__(self):
        return (
            f"Token(type={self.type}, value={self.value!r}, "
            f"line={self.line}, column={self.column})"
        )
