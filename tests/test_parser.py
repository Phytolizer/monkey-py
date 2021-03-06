from lexer import Lexer
from monkey_parser import Parser
import monkey_ast as ast
import pytest


class TestParser:
    def parse(self, text):
        lex = Lexer(text)
        par = Parser(lex)
        program = par.parse_program()
        self.check_parser_errors(par)
        return program

    def check_let_statement(self, stmt, name):
        assert stmt.token_literal() == "let"
        assert isinstance(stmt, ast.LetStatement)
        assert stmt.name.value == name
        assert stmt.name.token_literal() == name

    def check_parser_errors(self, parser):
        for error in parser.errors:
            print(f"parser error: {error}")
        assert len(parser.errors) == 0

    def check_integer_literal(self, actual, expected):
        assert isinstance(actual, ast.IntegerLiteral)
        assert actual.value == expected
        assert actual.token_literal() == str(expected)

    def check_identifier(self, exp, value):
        assert isinstance(exp, ast.Identifier)
        assert exp.value == value
        assert exp.token_literal() == value

    def check_boolean(self, exp, value):
        assert isinstance(exp, ast.Boolean)
        assert exp.value == value
        assert exp.token_literal() == str(value)

    def check_literal_expression(self, exp, expected):
        if isinstance(exp, int):
            self.check_integer_literal(exp, expected)
        elif isinstance(exp, str):
            self.check_identifier(exp, expected)
        elif isinstance(exp, bool):
            self.check_boolean(exp, expected)

    def check_infix_expression(self, exp, left, operator, right):
        assert isinstance(exp, ast.InfixExpression)
        self.check_literal_expression(exp.left, left)
        assert exp.operator == operator
        self.check_literal_expression(exp.right, right)

    @pytest.mark.parametrize(
        "text,expected_ident,expected_value",
        [
            ("let x = 5;", "x", 5),
            ("let y = true;", "y", True),
            ("let foobar = y;", "foobar", "y"),
        ],
    )
    def test_let_statements(self, text, expected_ident, expected_value):
        lex = Lexer(text)
        p = Parser(lex)

        program = p.parse_program()
        self.check_parser_errors(p)
        assert program is not None
        assert len(program.statements) == 1
        stmt = program.statements[0]
        self.check_let_statement(stmt, expected_ident)
        self.check_literal_expression(stmt.value, expected_value)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("return 5;", 5),
            ("return true;", True),
            ("return y;", "y"),
        ],
    )
    def test_return_statements(self, text, expected):
        program = self.parse(text)

        assert len(program.statements) == 1
        assert isinstance(program.statements[0], ast.ReturnStatement)
        assert program.statements[0].token_literal() == "return"
        self.check_literal_expression(program.statements[0].return_value, expected)

    def test_identifier_expression(self):
        text = "foobar;"

        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        self.check_literal_expression(stmt.expression, "foobar")

    def test_integer_literal_expression(self):
        text = "5;"

        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        self.check_literal_expression(stmt.expression, 5)

    def test_boolean_expression(self):
        text = "true;"
        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        self.check_literal_expression(stmt.expression, True)

    @pytest.mark.parametrize(
        "text,expected_operator,expected_literal",
        [
            ("!5;", "!", 5),
            ("-15;", "-", 15),
            ("!true;", "!", True),
            ("!false;", "!", False),
        ],
    )
    def test_prefix_expressions(self, text, expected_operator, expected_literal):
        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        assert isinstance(exp, ast.PrefixExpression)
        assert exp.operator == expected_operator
        self.check_literal_expression(exp.right, expected_literal)

    @pytest.mark.parametrize(
        "text,left,operator,right",
        [
            ("5 + 5;", 5, "+", 5),
            ("5 - 5;", 5, "-", 5),
            ("5 * 5;", 5, "*", 5),
            ("5 / 5;", 5, "/", 5),
            ("5 > 5;", 5, ">", 5),
            ("5 < 5;", 5, "<", 5),
            ("5 == 5;", 5, "==", 5),
            ("5 != 5;", 5, "!=", 5),
            ("true == true", True, "==", True),
            ("true != false", True, "!=", False),
            ("false == false", False, "==", False),
        ],
    )
    def test_infix_expressions(self, text, left, operator, right):
        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        self.check_infix_expression(stmt.expression, left, operator, right)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("-a * b", "((-a) * b)"),
            ("!-a", "(!(-a))"),
            ("a + b + c", "((a + b) + c)"),
            ("a + b - c", "((a + b) - c)"),
            ("a * b * c", "((a * b) * c)"),
            ("a * b / c", "((a * b) / c)"),
            ("a + b / c", "(a + (b / c))"),
            ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
            ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
            ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
            ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
            ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
            ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
            ("true", "true"),
            ("false", "false"),
            ("3 > 5 == false", "((3 > 5) == false)"),
            ("3 < 5 == true", "((3 < 5) == true)"),
            ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
            ("(5 + 5) * 2", "((5 + 5) * 2)"),
            ("2 / (5 + 5)", "(2 / (5 + 5))"),
            ("-(5 + 5)", "(-(5 + 5))"),
            ("!(true == true)", "(!(true == true))"),
            ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
            (
                "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
                "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
            ),
            ("add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"),
        ],
    )
    def test_operator_precedence(self, text, expected):
        program = self.parse(text)
        assert program.string() == expected

    def test_if_expression(self):
        text = "if (x < y) { x }"
        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        assert isinstance(exp, ast.IfExpression)
        self.check_infix_expression(exp.condition, "x", "<", "y")
        assert len(exp.consequence.statements) == 1
        consequence = exp.consequence.statements[0]
        assert isinstance(consequence, ast.ExpressionStatement)
        self.check_identifier(consequence.expression, "x")
        assert exp.alternative is None

    def test_if_else_expression(self):
        text = "if (x < y) { x } else { y }"
        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        assert isinstance(exp, ast.IfExpression)
        self.check_infix_expression(exp.condition, "x", "<", "y")
        assert len(exp.consequence.statements) == 1
        consequence = exp.consequence.statements[0]
        assert isinstance(consequence, ast.ExpressionStatement)
        self.check_identifier(consequence.expression, "x")
        assert exp.alternative is not None
        assert len(exp.alternative.statements) == 1
        alternative = exp.alternative.statements[0]
        assert isinstance(alternative, ast.ExpressionStatement)
        self.check_identifier(alternative.expression, "y")

    def test_function_literal(self):
        text = "fn(x, y) { x + y; }"
        program = self.parse(text)

        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        function = stmt.expression
        assert isinstance(function, ast.FunctionLiteral)
        assert len(function.parameters) == 2
        self.check_literal_expression(function.parameters[0], "x")
        self.check_literal_expression(function.parameters[1], "y")
        assert len(function.body.statements) == 1
        body_stmt = function.body.statements[0]
        assert isinstance(body_stmt, ast.ExpressionStatement)
        self.check_infix_expression(body_stmt.expression, "x", "+", "y")

    @pytest.mark.parametrize(
        "text,params",
        [
            ("fn() {};", []),
            ("fn(x) {};", ["x"]),
            ("fn(x, y, z) {};", ["x", "y", "z"]),
        ],
    )
    def test_function_parameters(self, text, params):
        program = self.parse(text)
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        function = stmt.expression
        assert isinstance(function, ast.FunctionLiteral)
        assert len(function.parameters) == len(params)
        for param, ident in zip(function.parameters, params):
            self.check_literal_expression(param, ident)

    def test_call_expression(self):
        text = "add(1, 2 * 3, 4 + 5)"
        program = self.parse(text)
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        assert isinstance(exp, ast.CallExpression)
        self.check_identifier(exp.function, "add")
        assert len(exp.arguments) == 3
        self.check_literal_expression(exp.arguments[0], 1)
        self.check_infix_expression(exp.arguments[1], 2, "*", 3)
        self.check_infix_expression(exp.arguments[2], 4, "+", 5)

    def test_string_literal(self):
        text = '"foobar"'
        program = self.parse(text)
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        assert isinstance(exp, ast.StringLiteral)
        assert exp.value == "foobar"

    def test_array_literal(self):
        text = "[1, 2 * 2, 3 + 3]"
        program = self.parse(text)
        assert isinstance(program.statements[0], ast.ExpressionStatement)
        assert isinstance(program.statements[0].expression, ast.ArrayLiteral)
        array = program.statements[0].expression
        assert len(array.elements) == 3
        self.check_integer_literal(array.elements[0], 1)
        self.check_infix_expression(array.elements[1], 2, "*", 2)
        self.check_infix_expression(array.elements[2], 3, "+", 3)

    def test_index_expression(self):
        text = "myArray[1 + 1]"
        program = self.parse(text)
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        index_exp = stmt.expression
        assert isinstance(index_exp, ast.IndexExpression)
        self.check_identifier(index_exp.left, "myArray")
        self.check_infix_expression(index_exp.index, 1, "+", 1)

    def test_hash_literals_string_keys(self):
        text = '{"one": 1, "two": 2, "three": 3}'
        program = self.parse(text)
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        hash = stmt.expression
        assert isinstance(hash, ast.HashLiteral)
        assert len(hash.pairs) == 3
        expected = {
            "one": 1,
            "two": 2,
            "three": 3,
        }
        for key, value in hash.pairs.items():
            assert isinstance(key, ast.StringLiteral)
            expected_value = expected[key.string()]
            self.check_integer_literal(value, expected_value)

    def test_hash_literals_integer_keys(self):
        text = "{2: 1, 1: 2, 3: 3}"
        program = self.parse(text)
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        hash = stmt.expression
        assert isinstance(hash, ast.HashLiteral)
        assert len(hash.pairs) == 3
        expected = {
            2: 1,
            1: 2,
            3: 3,
        }
        for key, value in hash.pairs.items():
            assert isinstance(key, ast.IntegerLiteral)
            expected_value = expected[key.value]
            self.check_integer_literal(value, expected_value)

    def test_hash_literals_boolean_keys(self):
        text = "{true: 1, false: 2}"
        program = self.parse(text)
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        hash = stmt.expression
        assert isinstance(hash, ast.HashLiteral)
        assert len(hash.pairs) == 2
        expected = {
            True: 1,
            False: 2,
        }
        for key, value in hash.pairs.items():
            assert isinstance(key, ast.Boolean)
            expected_value = expected[key.value]
            self.check_integer_literal(value, expected_value)

    def test_empty_hash_literal(self):
        text = "{}"
        program = self.parse(text)
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        hash = stmt.expression
        assert isinstance(hash, ast.HashLiteral)
        assert len(hash.pairs) == 0

    def test_hash_literals_with_expressions(self):
        text = '{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}'
        program = self.parse(text)
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        hash = stmt.expression
        assert isinstance(hash, ast.HashLiteral)
        assert len(hash.pairs) == 3
        tests = {
            "one": lambda e: self.check_infix_expression(e, 0, "+", 1),
            "two": lambda e: self.check_infix_expression(e, 10, "-", 8),
            "three": lambda e: self.check_infix_expression(e, 15, "/", 5),
        }
        for key, value in hash.pairs.items():
            assert isinstance(key, ast.StringLiteral)
            test_func = tests[key.string()]
            test_func(value)
