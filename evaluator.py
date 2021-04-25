import lexer
import object
import parser
import ast
import unittest

TRUE = object.Boolean(True)
FALSE = object.Boolean(False)
NULL = object.Null()

def eval_node(node):
    if isinstance(node, ast.Program):
        return eval_statements(node.statements)
    elif isinstance(node, ast.ExpressionStatement):
        return eval_node(node.expression)
    elif isinstance(node, ast.PrefixExpression):
        right = eval_node(node.right)
        return eval_prefix_expression(node.operator, right)
    elif isinstance(node, ast.IntegerLiteral):
        return object.Integer(node.value)
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

class EvaluatorTests(unittest.TestCase):
    def check_integer_object(self, obj, expected):
        self.assertIsInstance(obj, object.Integer)
        self.assertEqual(obj.value, expected)
    
    def check_boolean_object(self, obj, expected):
        self.assertIs(obj, expected)

    def eval_setup(self, text):
        l = lexer.Lexer(text)
        p = parser.Parser(l)
        program = p.parse_program()
        return eval_node(program)

    def test_eval_integer_expression(self):
        tests = (
            ("5", 5),
            ("10", 10),
        )
        for i, tt in enumerate(tests):
            with self.subTest(i=i):
                evaluated = self.eval_setup(tt[0])
                self.check_integer_object(evaluated, tt[1])
    
    def test_eval_boolean_expression(self):
        tests = (
            ("true", TRUE),
            ("false", FALSE),
        )
        for i, tt in enumerate(tests):
            evaluated = self.eval_setup(tt[0])
            self.check_boolean_object(evaluated, tt[1])
    
    def test_eval_bang_operator(self):
        tests = (
            ("!true", FALSE),
            ("!false", TRUE),
            ("!5", FALSE),
            ("!!true", TRUE),
            ("!!false", FALSE),
            ("!!5", TRUE),
        )

        for i, tt in enumerate(tests):
            with self.subTest(i=i):
                evaluated = self.eval_setup(tt[0])
                self.check_boolean_object(evaluated, tt[1])

if __name__ == "__main__":
    unittest.main()
