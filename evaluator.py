import monkey_object
import monkey_ast as ast
import unittest

TRUE = monkey_object.Boolean(True)
FALSE = monkey_object.Boolean(False)
NULL = monkey_object.Null()


def eval_node(node):
    if isinstance(node, ast.Program):
        return eval_statements(node.statements)
    elif isinstance(node, ast.ExpressionStatement):
        return eval_node(node.expression)
    elif isinstance(node, ast.InfixExpression):
        left = eval_node(node.left)
        right = eval_node(node.right)
        return eval_infix_expression(node.operator, left, right)
    elif isinstance(node, ast.PrefixExpression):
        right = eval_node(node.right)
        return eval_prefix_expression(node.operator, right)
    elif isinstance(node, ast.IntegerLiteral):
        return monkey_object.Integer(node.value)
    elif isinstance(node, ast.Boolean):
        return native_bool_to_boolean_object(node.value)
    else:
        return None


def native_bool_to_boolean_object(obj):
    if obj:
        return TRUE
    else:
        return FALSE


def eval_statements(stmts):
    result = None
    for stmt in stmts:
        result = eval_node(stmt)
    return result


def eval_prefix_expression(operator, right):
    if operator == "!":
        return eval_bang_operator_expression(right)
    elif operator == "-":
        return eval_minus_prefix_operator_expression(right)
    else:
        return NULL


def eval_infix_expression(operator, left, right):
    if (
        left.type() == monkey_object.ObjectType.INTEGER
        and right.type() == monkey_object.ObjectType.INTEGER
    ):
        return eval_integer_infix_expression(operator, left, right)
    elif operator == "==":
        return native_bool_to_boolean_object(left == right)
    elif operator == "!=":
        return native_bool_to_boolean_object(left != right)
    else:
        return NULL


def eval_integer_infix_expression(operator, left, right):
    if operator == "+":
        return monkey_object.Integer(left.value + right.value)
    elif operator == "-":
        return monkey_object.Integer(left.value - right.value)
    elif operator == "*":
        return monkey_object.Integer(left.value * right.value)
    elif operator == "/":
        return monkey_object.Integer(left.value / right.value)
    elif operator == "<":
        return native_bool_to_boolean_object(left.value < right.value)
    elif operator == ">":
        return native_bool_to_boolean_object(left.value > right.value)
    elif operator == "==":
        return native_bool_to_boolean_object(left.value == right.value)
    elif operator == "!=":
        return native_bool_to_boolean_object(left.value != right.value)
    else:
        return NULL


def eval_bang_operator_expression(right):
    if right is TRUE:
        return FALSE
    elif right is FALSE:
        return TRUE
    elif right is NULL:
        return FALSE
    else:
        return FALSE


def eval_minus_prefix_operator_expression(right):
    if right.type() != monkey_object.ObjectType.INTEGER:
        return NULL
    value = right.value
    return monkey_object.Integer(-value)


if __name__ == "__main__":
    unittest.main()
