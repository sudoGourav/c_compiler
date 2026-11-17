from compiler.ast_nodes import *


def print_ast(node, level=0):
    indent = "    " * level

    if node is None:
        print(indent + "None")
        return

    if isinstance(node, Program):
        print(indent + "Program")
        for item in node.statements:
            print_ast(item, level + 1)

    elif isinstance(node, Declaration):
        print(indent + "Declaration")
        print(indent + "    Type:", node.data_type)
        print(indent + "    Name:", node.name)
        if node.value is not None:
            print(indent + "    Value:")
            print_ast(node.value, level + 2)

    elif isinstance(node, Assignment):
        print(indent + "Assignment")
        print(indent + "    Name:", node.name)
        print(indent + "    Operator:", node.operator)
        if node.value is not None:
            print(indent + "    Value:")
            print_ast(node.value, level + 2)

    elif isinstance(node, BinaryExpression):
        print(indent + "BinaryExpression")
        print(indent + "    Operator:", node.operator)
        print(indent + "    Left:")
        print_ast(node.left, level + 2)
        print(indent + "    Right:")
        print_ast(node.right, level + 2)

    elif isinstance(node, UnaryExpression):
        print(indent + "UnaryExpression")
        print(indent + "    Operator:", node.operator)
        print(indent + "    Operand:")
        print_ast(node.operand, level + 2)

    elif isinstance(node, Number):
        print(indent + "Number:", node.value)

    elif isinstance(node, Identifier):
        print(indent + "Identifier:", node.name)

    elif isinstance(node, Literal):
        print(indent + f"{node.literal_type.title()}:", node.value)

    elif isinstance(node, Condition):
        print(indent + "Condition")
        print(indent + "    Operator:", node.operator)
        print(indent + "    Left:")
        print_ast(node.left, level + 2)
        print(indent + "    Right:")
        print_ast(node.right, level + 2)

    elif isinstance(node, LogicalExpression):
        print(indent + "LogicalExpression")
        print(indent + "    Operator:", node.operator)
        print(indent + "    Left:")
        print_ast(node.left, level + 2)
        print(indent + "    Right:")
        print_ast(node.right, level + 2)

    elif isinstance(node, IfStatement):
        print(indent + "IfStatement")
        print(indent + "    Condition:")
        print_ast(node.condition, level + 2)
        print(indent + "    Then:")
        print_ast(node.then_branch, level + 2)
        if node.else_branch is not None:
            print(indent + "    Else:")
            print_ast(node.else_branch, level + 2)

    elif isinstance(node, WhileStatement):
        print(indent + "WhileStatement")
        print(indent + "    Condition:")
        print_ast(node.condition, level + 2)
        print(indent + "    Body:")
        print_ast(node.body, level + 2)

    elif isinstance(node, ForStatement):
        print(indent + "ForStatement")
        if node.initialization is not None:
            print(indent + "    Initialization:")
            print_ast(node.initialization, level + 2)
        if node.condition is not None:
            print(indent + "    Condition:")
            print_ast(node.condition, level + 2)
        if node.update is not None:
            print(indent + "    Update:")
            print_ast(node.update, level + 2)
        print(indent + "    Body:")
        print_ast(node.body, level + 2)

    elif isinstance(node, DoWhileStatement):
        print(indent + "DoWhileStatement")
        print(indent + "    Body:")
        print_ast(node.body, level + 2)
        print(indent + "    Condition:")
        print_ast(node.condition, level + 2)

    elif isinstance(node, Block):
        print(indent + "Block")
        for item in node.statements:
            print_ast(item, level + 1)

    elif isinstance(node, ReturnStatement):
        print(indent + "ReturnStatement")
        if node.value is not None:
            print(indent + "    Value:")
            print_ast(node.value, level + 2)

    elif isinstance(node, ExpressionStatement):
        print(indent + "ExpressionStatement")
        print_ast(node.expression, level + 1)

    else:
        print(indent + "Unknown Node:", type(node).__name__)
