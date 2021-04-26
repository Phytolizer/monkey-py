import monkey_object
import monkey_ast as ast
from environment import Environment

TRUE = monkey_object.Boolean(True)
FALSE = monkey_object.Boolean(False)
NULL = monkey_object.Null()


def is_error(obj):
    return obj is not None and obj.type() == monkey_object.ObjectType.ERROR


def eval_node(node, env):
    if isinstance(node, ast.Program):
        return eval_program(node, env)
    elif isinstance(node, ast.BlockStatement):
        return eval_block_statement(node, env)
    elif isinstance(node, ast.LetStatement):
        val = eval_node(node.value, env)
        if is_error(val):
            return val
        env.set(node.name.value, val)
    elif isinstance(node, ast.ReturnStatement):
        val = eval_node(node.return_value, env)
        if is_error(val):
            return val
        return monkey_object.ReturnValue(val)
    elif isinstance(node, ast.ExpressionStatement):
        return eval_node(node.expression, env)
    elif isinstance(node, ast.CallExpression):
        function = eval_node(node.function, env)
        if is_error(function):
            return function
        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]
        return apply_function(function, args)
    elif isinstance(node, ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return monkey_object.Function(params, body, env)
    elif isinstance(node, ast.IfExpression):
        return eval_if_expression(node, env)
    elif isinstance(node, ast.InfixExpression):
        left = eval_node(node.left, env)
        if is_error(left):
            return left
        right = eval_node(node.right, env)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    elif isinstance(node, ast.PrefixExpression):
        right = eval_node(node.right, env)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    elif isinstance(node, ast.IntegerLiteral):
        return monkey_object.Integer(node.value)
    elif isinstance(node, ast.Boolean):
        return native_bool_to_boolean_object(node.value)
    elif isinstance(node, ast.Identifier):
        return eval_identifier(node, env)
    elif isinstance(node, ast.StringLiteral):
        return monkey_object.String(node.value)
    else:
        return None


def native_bool_to_boolean_object(obj):
    if obj:
        return TRUE
    else:
        return FALSE


def is_truthy(obj):
    return obj is not FALSE and obj is not NULL


def eval_program(program, env):
    result = None
    for stmt in program.statements:
        result = eval_node(stmt, env)

        if isinstance(result, monkey_object.ReturnValue):
            if result.value is None:
                return NULL
            else:
                return result.value
        if isinstance(result, monkey_object.Error):
            return result

    return result


def eval_block_statement(bs, env):
    result = None
    for stmt in bs.statements:
        result = eval_node(stmt, env)

        if isinstance(result, monkey_object.ReturnValue) or isinstance(
            result, monkey_object.Error
        ):
            return result

    return result


def eval_if_expression(node, env):
    condition = eval_node(node.condition, env)
    if is_truthy(condition):
        return eval_node(node.consequence, env)
    elif node.alternative is not None:
        return eval_node(node.alternative, env)
    else:
        return NULL


def eval_prefix_expression(operator, right):
    if operator == "!":
        return eval_bang_operator_expression(right)
    elif operator == "-":
        return eval_minus_prefix_operator_expression(right)
    else:
        return NULL  # unreachable?


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
    elif left.type() != right.type():
        return monkey_object.Error(
            f"type mismatch: {left.type()} {operator} {right.type()}"
        )
    else:
        return monkey_object.Error(
            f"unknown operator: {left.type()} {operator} {right.type()}"
        )


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
        return monkey_object.Error(f"unknown operator: -{right.type()}")
    value = right.value
    return monkey_object.Integer(-value)


def eval_identifier(node, env):
    try:
        val = env.get(node.value)
    except KeyError:
        return monkey_object.Error(f"identifier not found: {node.value}")
    return val


def eval_expressions(exps, env):
    result = []
    for e in exps:
        evaluated = eval_node(e, env)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def apply_function(function, args):
    if not isinstance(function, monkey_object.Function):
        return monkey_object.Error(f"not a function: {function.type()}")
    extended_env = extend_function_env(function, args)
    evaluated = eval_node(function.body, extended_env)
    return unwrap_return_value(evaluated)


def extend_function_env(function, args):
    env = Environment(function.env)

    for arg, param in zip(args, function.parameters):
        env.set(param.value, arg)

    return env


def unwrap_return_value(obj):
    if isinstance(obj, monkey_object.ReturnValue):
        return obj.value
    return obj
