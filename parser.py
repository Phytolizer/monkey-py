from enum import IntEnum, auto
from tokens import Token, TokenType
import ast
import unittest

class Precedence(IntEnum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()

PRECEDENCES = {
    TokenType.Eq: Precedence.EQUALS,
    TokenType.NotEq: Precedence.EQUALS,
    TokenType.Less: Precedence.LESSGREATER,
    TokenType.Greater: Precedence.LESSGREATER,
    TokenType.Plus: Precedence.SUM,
    TokenType.Minus: Precedence.SUM,
    TokenType.Star: Precedence.PRODUCT,
    TokenType.Slash: Precedence.PRODUCT,
}

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.cur_token = Token()
        self.peek_token = Token()
        self.next_token()
        self.next_token()
        self.errors = []
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}

        self.register_prefix(TokenType.Ident, self.parse_identifier)
        self.register_prefix(TokenType.Num, self.parse_integer_literal)
        self.register_prefix(TokenType.Bang, self.parse_prefix_expression)
        self.register_prefix(TokenType.Minus, self.parse_prefix_expression)
        self.register_prefix(TokenType.TRUE, self.parse_boolean)
        self.register_prefix(TokenType.FALSE, self.parse_boolean)
        self.register_prefix(TokenType.LParen, self.parse_grouped_expression)
        self.register_prefix(TokenType.If, self.parse_if_expression)
        self.register_prefix(TokenType.Fn, self.parse_function_literal)
        
        self.register_infix(TokenType.Plus, self.parse_infix_expression)
        self.register_infix(TokenType.Minus, self.parse_infix_expression)
        self.register_infix(TokenType.Star, self.parse_infix_expression)
        self.register_infix(TokenType.Slash, self.parse_infix_expression)
        self.register_infix(TokenType.Eq, self.parse_infix_expression)
        self.register_infix(TokenType.NotEq, self.parse_infix_expression)
        self.register_infix(TokenType.Less, self.parse_infix_expression)
        self.register_infix(TokenType.Greater, self.parse_infix_expression)
    
    def peek_precedence(self):
        try:
            return PRECEDENCES[self.peek_token.type]
        except KeyError:
            return Precedence.LOWEST
    
    def cur_precedence(self):
        try:
            return PRECEDENCES[self.cur_token.type]
        except KeyError:
            return Precedence.LOWEST
    
    def register_prefix(self, type, fn):
        self.prefix_parse_fns[type] = fn
    
    def register_infix(self, type, fn):
        self.infix_parse_fns[type] = fn

    def peek_error(self, type):
        self.errors.append(
            f"expected next token to be {type}, got {self.peek_token.type} instead"
        )
    
    def no_prefix_parse_fn_error(self, type):
        self.errors.append(
            f"no prefix parse fn for {type} found"
        )
    
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def cur_token_is(self, type):
        return self.cur_token.type == type
    
    def peek_token_is(self, type):
        return self.peek_token.type == type

    def expect_peek(self, type):
        if self.peek_token_is(type):
            self.next_token()
            return True
        else:
            self.peek_error(type)
            return False
    
    def parse_program(self):
        program = ast.Program([])

        while self.cur_token.type != TokenType.Eof:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()
        
        return program
    
    def parse_statement(self):
        if self.cur_token.type == TokenType.Let:
            return self.parse_let_statement()
        elif self.cur_token.type == TokenType.Return:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()
    
    def parse_let_statement(self):
        tok = self.cur_token

        if not self.expect_peek(TokenType.Ident):
            return None
        
        name = ast.Identifier(self.cur_token, self.cur_token.literal)

        if not self.expect_peek(TokenType.Assign):
            return None
        
        while not self.cur_token_is(TokenType.Semicolon):
            self.next_token()
        
        return ast.LetStatement(tok, name, None)
    
    def parse_return_statement(self):
        token = self.cur_token

        self.next_token()

        while not self.cur_token_is(TokenType.Semicolon):
            self.next_token()
        
        return ast.ReturnStatement(token, None)
    
    def parse_expression_statement(self):
        token = self.cur_token
        expression = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.Semicolon):
            self.next_token()

        return ast.ExpressionStatement(token, expression)
    
    def parse_expression(self, precedence):
        try:
            prefix = self.prefix_parse_fns[self.cur_token.type]
        except KeyError:
            self.no_prefix_parse_fn_error(self.cur_token.type)
            return None

        left_exp = prefix()

        while not self.peek_token_is(TokenType.Semicolon) and precedence < self.peek_precedence():
            try:
                infix = self.infix_parse_fns[self.peek_token.type]
            except KeyError:
                return left_exp
            
            self.next_token()
            left_exp = infix(left_exp)

        return left_exp

    def parse_function_literal(self):
        token = self.cur_token
        if not self.expect_peek(TokenType.LParen):
            return None
        parameters = self.parse_function_parameters()
        if not self.expect_peek(TokenType.LBrace):
            return None
        body = self.parse_block_statement()
        return ast.FunctionLiteral(token, parameters, body)
    
    def parse_function_parameters(self):
        identifiers = []
        if self.peek_token_is(TokenType.RParen):
            self.next_token()
            return identifiers
        self.next_token()
        ident = ast.Identifier(self.cur_token, self.cur_token.literal)
        identifiers.append(ident)
        while self.peek_token_is(TokenType.Comma):
            self.next_token()
            self.next_token()
            ident = ast.Identifier(self.cur_token, self.cur_token.literal)
            identifiers.append(ident)
        if not self.expect_peek(TokenType.RParen):
            return None
        return identifiers

    def parse_if_expression(self):
        token = self.cur_token

        if not self.expect_peek(TokenType.LParen):
            return None
        self.next_token()
        condition = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RParen):
            return None
        if not self.expect_peek(TokenType.LBrace):
            return None
        
        consequence = self.parse_block_statement()

        alternative = None
        if self.peek_token_is(TokenType.Else):
            self.next_token()

            if not self.expect_peek(TokenType.LBrace):
                return Nont
            alternative = self.parse_block_statement()

        return ast.IfExpression(token, condition, consequence, alternative)
    
    def parse_block_statement(self):
        token = self.cur_token
        statements = []
        self.next_token()

        while not self.cur_token_is(TokenType.RBrace) and not self.cur_token_is(TokenType.Eof):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.next_token()
        return ast.BlockStatement(token, statements)
    
    def parse_infix_expression(self, left):
        token = self.cur_token
        operator = self.cur_token.literal

        precedence = self.cur_precedence()
        self.next_token()
        right = self.parse_expression(precedence)

        return ast.InfixExpression(token, left, operator, right)

    def parse_prefix_expression(self):
        token = self.cur_token
        operator = self.cur_token.literal
        self.next_token()
        right = self.parse_expression(Precedence.PREFIX)

        return ast.PrefixExpression(token, operator, right)

    def parse_identifier(self):
        return ast.Identifier(self.cur_token, self.cur_token.literal)
    
    def parse_integer_literal(self):
        token = self.cur_token

        try:
            value = int(self.cur_token.literal)
        except ValueError:
            self.errors.append(
                f"could not parse '{self.cur_token.literal}' as integer"
            )
            return None
        
        return ast.IntegerLiteral(token, value)
    
    def parse_boolean(self):
        return ast.Boolean(self.cur_token, self.cur_token_is(TokenType.TRUE))
    
    def parse_grouped_expression(self):
        self.next_token()
        exp = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(TokenType.RParen):
            return None
        return exp
    
class ParserTests(unittest.TestCase):
    def check_let_statement(self, stmt, name):
        self.assertEqual(stmt.token_literal(), "let")
        self.assertIsInstance(stmt, ast.LetStatement)
        self.assertEqual(stmt.name.value, name)
        self.assertEqual(stmt.name.token_literal(), name)

    def check_parser_errors(self, parser):
        for error in parser.errors:
            print(f"parser error: {error}")
        self.assertEqual(len(parser.errors), 0)
    
    def check_integer_literal(self, actual, expected):
        self.assertIsInstance(actual, ast.IntegerLiteral)
        self.assertEqual(actual.value, expected)
        self.assertEqual(actual.token_literal(), str(expected))
    
    def check_identifier(self, exp, value):
        self.assertIsInstance(exp, ast.Identifier)
        self.assertEqual(exp.value, value)
        self.assertEqual(exp.token_literal(), value)
    
    def check_boolean(self, exp, value):
        self.assertIsInstance(exp, ast.Boolean)
        self.assertEqual(exp.value, value)
        self.assertEqual(exp.token_literal(), str(value))
    
    def check_literal_expression(self, exp, expected):
        if isinstance(exp, int):
            self.check_integer_literal(exp, expected)
        elif isinstance(exp, str):
            self.check_identifier(exp, expected)
        elif isinstance(exp, bool):
            self.check_boolean(exp, expected)
    
    def check_infix_expression(self, exp, left, operator, right):
        self.assertIsInstance(exp, ast.InfixExpression)
        self.check_literal_expression(exp.left, left)
        self.assertEqual(exp.operator, operator)
        self.check_literal_expression(exp.right, right)

    def test_let_statements(self):
        text = """
        let x = 5;
        let y = 10;
        let foobar = 838383;
        """

        l = Lexer(text)
        p = Parser(l)

        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 3)
        tests = (
            ("x"),
            ("y"),
            ("foobar"),
        )

        for i, tt in enumerate(tests):
            with self.subTest(i=i):
                stmt = program.statements[i]
                self.check_let_statement(stmt, tt)
    
    def test_return_statements(self):
        text = """
        return 5;
        return 10;
        return 993322;
        """

        l = Lexer(text)
        p = Parser(l)

        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 3)
        for i, stmt in enumerate(program.statements):
            with self.subTest(i=i):
                self.assertIsInstance(stmt, ast.ReturnStatement)
                self.assertEqual(stmt.token_literal(), "return")
    
    def test_identifier_expression(self):
        text = "foobar;"

        l = Lexer(text)
        p = Parser(l)

        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 1)    
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.check_literal_expression(stmt.expression, "foobar")

    def test_integer_literal_expression(self):
        text = "5;"

        l = Lexer(text)
        p = Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.check_literal_expression(stmt.expression, 5)
    
    def test_boolean_expression(self):
        text = "true;"
        l = Lexer(text)
        p = Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.check_literal_expression(stmt.expression, True)
    
    def test_prefix_expressions(self):
        prefix_tests = (
            ("!5;", "!", 5),
            ("-15;", "-", 15),
            ("!true;", "!", True),
            ("!false;", "!", False),
        )

        for i, tt in enumerate(prefix_tests):
            with self.subTest(i=i):
                l = Lexer(tt[0])
                p = Parser(l)
                program = p.parse_program()
                self.check_parser_errors(p)

                self.assertEqual(len(program.statements), 1)
                stmt = program.statements[0]
                self.assertIsInstance(stmt, ast.ExpressionStatement)
                exp = stmt.expression
                self.assertIsInstance(exp, ast.PrefixExpression)
                self.assertEqual(exp.operator, tt[1])
                self.check_literal_expression(exp.right, tt[2])
            
    def test_infix_expressions(self):
        infix_tests = (
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
        )
        for i, tt in enumerate(infix_tests):
            with self.subTest(i=i):
                l = Lexer(tt[0])
                p = Parser(l)
                program = p.parse_program()
                self.check_parser_errors(p)

                self.assertEqual(len(program.statements), 1)
                stmt = program.statements[0]
                self.assertIsInstance(stmt, ast.ExpressionStatement)
                self.check_infix_expression(stmt.expression, *tt[1:])
    
    def test_operator_precedence(self):
        tests = (
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
        )

        for i, tt in enumerate(tests):
            with self.subTest(i=i):
                l = Lexer(tt[0])
                p = Parser(l)
                program = p.parse_program()
                self.check_parser_errors(p)
                self.assertEqual(program.string(), tt[1])
    
    def test_if_expression(self):
        text = "if (x < y) { x }"
        l = Lexer(text)
        p = Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        self.assertIsInstance(exp, ast.IfExpression)
        self.check_infix_expression(exp.condition, "x", "<", "y")
        self.assertEqual(len(exp.consequence.statements), 1)
        consequence = exp.consequence.statements[0]
        self.assertIsInstance(consequence, ast.ExpressionStatement)
        self.check_identifier(consequence.expression, "x")
        self.assertIsNone(exp.alternative)
    
    def test_if_else_expression(self):
        text = "if (x < y) { x } else { y }"
        l = Lexer(text)
        p = Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        self.assertIsInstance(exp, ast.IfExpression)
        self.check_infix_expression(exp.condition, "x", "<", "y")
        self.assertEqual(len(exp.consequence.statements), 1)
        consequence = exp.consequence.statements[0]
        self.assertIsInstance(consequence, ast.ExpressionStatement)
        self.check_identifier(consequence.expression, "x")
        self.assertIsNotNone(exp.alternative)
        self.assertEqual(len(exp.alternative.statements), 1)
        alternative = exp.alternative.statements[0]
        self.assertIsInstance(alternative, ast.ExpressionStatement)
        self.check_identifier(alternative.expression, "y")
    
    def test_function_literal(self):
        text = "fn(x, y) { x + y; }"
        l = Lexer(text)
        p = Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        function = stmt.expression
        self.assertIsInstance(function, ast.FunctionLiteral)
        self.assertEqual(len(function.parameters), 2)
        self.check_literal_expression(function.parameters[0], "x")
        self.check_literal_expression(function.parameters[1], "y")
        self.assertEqual(len(function.body.statements), 1)
        body_stmt = function.body.statements[0]
        self.assertIsInstance(body_stmt, ast.ExpressionStatement)
        self.check_infix_expression(body_stmt.expression, "x", "+", "y")
    
    def test_function_parameters_parsing(self):
        tests = (
            ("fn() {};", []),
            ("fn(x) {};", ["x"]),
            ("fn(x, y, z) {};", ["x", "y", "z"]),
        )
        for i, tt in enumerate(tests):
            with self.subTest(i=i):
                l = Lexer(tt[0])
                p = Parser(l)
                program = p.parse_program()
                self.check_parser_errors(p)
                stmt = program.statements[0]
                self.assertIsInstance(stmt, ast.ExpressionStatement)
                function = stmt.expression
                self.assertIsInstance(function, ast.FunctionLiteral)
                self.assertEqual(len(function.parameters), len(tt[1]))
                for param, ident in zip(function.parameters, tt[1]):
                    self.check_literal_expression(param, ident)

if __name__ == "__main__":
    from lexer import Lexer
    unittest.main()
