from dataclasses import dataclass, field
from typing import Optional, List, Any


@dataclass
class Program:
    statements: List[Any] = field(default_factory=list)


@dataclass
class Declaration:
    data_type: str
    name: str
    value: Optional[Any] = None


@dataclass
class Assignment:
    name: str
    operator: str
    value: Optional[Any] = None


@dataclass
class BinaryExpression:
    left: Any
    operator: str
    right: Any


@dataclass
class UnaryExpression:
    operator: str
    operand: Any


@dataclass
class Number:
    value: str


@dataclass
class Identifier:
    name: str


@dataclass
class Literal:
    value: str
    literal_type: str


@dataclass
class Condition:
    left: Any
    operator: str
    right: Any


@dataclass
class LogicalExpression:
    left: Any
    operator: str
    right: Any


@dataclass
class IfStatement:
    condition: Any
    then_branch: Any
    else_branch: Optional[Any] = None


@dataclass
class WhileStatement:
    condition: Any
    body: Any


@dataclass
class ForStatement:
    initialization: Optional[Any]
    condition: Optional[Any]
    update: Optional[Any]
    body: Any


@dataclass
class DoWhileStatement:
    body: Any
    condition: Any


@dataclass
class Block:
    statements: List[Any] = field(default_factory=list)


@dataclass
class ReturnStatement:
    value: Optional[Any] = None


@dataclass
class ExpressionStatement:
    expression: Any
