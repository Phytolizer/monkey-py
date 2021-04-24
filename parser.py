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
        ident = stmt.expression
        self.assertIsInstance(ident, ast.Identifier)
        self.assertEqual(ident.value, "foobar")
        self.assertEqual(ident.token_literal(), "foobar")

    def test_integer_literal_expression(self):
        text = "5;"

        l = Lexer(text)
        p = Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        literal = stmt.expression
        self.assertIsInstance(literal, ast.IntegerLiteral)
        self.assertEqual(literal.value, 5)
        self.assertEqual(literal.token_literal(), "5")
    
    def test_prefix_expressions(self):
        prefix_tests = (
            ("!5;", "!", 5),
            ("-15;", "-", 15),
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
                self.check_integer_literal(exp.right, tt[2])
            
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
                exp = stmt.expression
                self.assertIsInstance(exp, ast.InfixExpression)
                self.check_integer_literal(exp.left, tt[1])
                self.assertEqual(exp.operator, tt[2])
                self.check_integer_literal(exp.right, tt[3])

if __name__ == "__main__":
    from lexer import Lexer
    unittest.main()
