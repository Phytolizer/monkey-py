from enum import IntEnum, auto
from tokens import Token, TokenType
import monkey_ast as ast


class Precedence(IntEnum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()
    INDEX = auto()


PRECEDENCES = {
    TokenType.Eq: Precedence.EQUALS,
    TokenType.NotEq: Precedence.EQUALS,
    TokenType.Less: Precedence.LESSGREATER,
    TokenType.Greater: Precedence.LESSGREATER,
    TokenType.Plus: Precedence.SUM,
    TokenType.Minus: Precedence.SUM,
    TokenType.Star: Precedence.PRODUCT,
    TokenType.Slash: Precedence.PRODUCT,
    TokenType.LParen: Precedence.CALL,
    TokenType.LBracket: Precedence.INDEX,
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
        self.register_prefix(TokenType.String, self.parse_string_literal)
        self.register_prefix(TokenType.LBracket, self.parse_array_literal)

        self.register_infix(TokenType.Plus, self.parse_infix_expression)
        self.register_infix(TokenType.Minus, self.parse_infix_expression)
        self.register_infix(TokenType.Star, self.parse_infix_expression)
        self.register_infix(TokenType.Slash, self.parse_infix_expression)
        self.register_infix(TokenType.Eq, self.parse_infix_expression)
        self.register_infix(TokenType.NotEq, self.parse_infix_expression)
        self.register_infix(TokenType.Less, self.parse_infix_expression)
        self.register_infix(TokenType.Greater, self.parse_infix_expression)
        self.register_infix(TokenType.LParen, self.parse_call_expression)
        self.register_infix(TokenType.LBracket, self.parse_index_expression)

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
        self.errors.append(f"no prefix parse fn for {type} found")

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

        self.next_token()
        value = self.parse_expression(Precedence.LOWEST)
        if self.peek_token_is(TokenType.Semicolon):
            self.next_token()

        return ast.LetStatement(tok, name, value)

    def parse_return_statement(self):
        token = self.cur_token

        self.next_token()

        return_value = self.parse_expression(Precedence.LOWEST)
        if self.peek_token_is(TokenType.Semicolon):
            self.next_token()

        return ast.ReturnStatement(token, return_value)

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

        while (
            not self.peek_token_is(TokenType.Semicolon)
            and precedence < self.peek_precedence()
        ):
            try:
                infix = self.infix_parse_fns[self.peek_token.type]
            except KeyError:
                return left_exp

            self.next_token()
            left_exp = infix(left_exp)

        return left_exp

    def parse_call_expression(self, function):
        token = self.cur_token
        arguments = self.parse_expression_list(TokenType.RParen)
        return ast.CallExpression(token, function, arguments)

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
                return None
            alternative = self.parse_block_statement()

        return ast.IfExpression(token, condition, consequence, alternative)

    def parse_block_statement(self):
        token = self.cur_token
        statements = []
        self.next_token()

        while not self.cur_token_is(TokenType.RBrace) and not self.cur_token_is(
            TokenType.Eof
        ):
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
            self.errors.append(f"could not parse '{self.cur_token.literal}' as integer")
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

    def parse_string_literal(self):
        return ast.StringLiteral(self.cur_token, self.cur_token.literal)

    def parse_expression_list(self, end):
        list = []
        if self.peek_token_is(end):
            self.next_token()
            return list

        self.next_token()
        list.append(self.parse_expression(Precedence.LOWEST))
        while self.peek_token_is(TokenType.Comma):
            self.next_token()
            self.next_token()
            list.append(self.parse_expression(Precedence.LOWEST))

        if not self.expect_peek(end):
            return None
        return list

    def parse_array_literal(self):
        token = self.cur_token
        elements = self.parse_expression_list(TokenType.RBracket)
        return ast.ArrayLiteral(token, elements)
    
    def parse_index_expression(self, left):
        token = self.cur_token
        self.next_token()
        index = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(TokenType.RBracket):
            return None
        return ast.IndexExpression(token, left, index)
