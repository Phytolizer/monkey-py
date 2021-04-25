import lexer
import object
import parser
import ast
import unittest

def eval_node(node):
    if isinstance(node, ast.Program):
        return eval_statements(node.statements)
    elif isinstance(node, ast.ExpressionStatement):
        return eval_node(node.expression)
    elif isinstance(node, ast.IntegerLiteral):
        return object.Integer(node.value)
    else:
        return None

def eval_statements(stmts):
    result = None
    for stmt in stmts:
        result = eval_node(stmt)
    return result

class EvaluatorTests(unittest.TestCase):
    def check_integer_object(self, obj, expected):
        self.assertIsInstance(obj, object.Integer)
        self.assertEqual(obj.value, expected)
    
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

if __name__ == "__main__":
    unittest.main()
