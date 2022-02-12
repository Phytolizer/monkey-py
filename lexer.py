import pytest
from tokens import TokenType, Token
import tokens


def is_letter(ch):
    return "a" <= ch and ch <= "z" or "A" <= ch and ch <= "Z" or ch == "_"


def is_whitespace(ch):
    return ch == " " or ch == "\t" or ch == "\r" or ch == "\n"


def is_digit(ch):
    return "0" <= ch and ch <= "9"


class Lexer:
    def __init__(self, source):
        self.input = source
        self.position = 0
        self.read_position = 0
        self.ch = "\0"

        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = "\0"
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self):
        if self.read_position >= len(self.input):
            return "\0"
        else:
            return self.input[self.read_position]

    def skip_whitespace(self):
        while is_whitespace(self.ch):
            self.read_char()

    def read_identifier(self):
        position = self.position
        while is_letter(self.ch):
            self.read_char()

        return self.input[position : self.position]

    def read_number(self):
        position = self.position
        while is_digit(self.ch):
            self.read_char()

        return self.input[position : self.position]

    def next_token(self):
        tok = Token(TokenType.ILLEGAL, "")

        self.skip_whitespace()

        if self.ch == "=":
            if self.peek_char() == "=":
                self.read_char()
                tok = Token(TokenType.EQ, "==")
            else:
                tok = Token(TokenType.ASSIGN, "=")
        elif self.ch == "+":
            tok = Token(TokenType.PLUS, "+")
        elif self.ch == ",":
            tok = Token(TokenType.COMMA, ",")
        elif self.ch == ";":
            tok = Token(TokenType.SEMICOLON, ";")
        elif self.ch == "(":
            tok = Token(TokenType.LPAREN, "(")
        elif self.ch == ")":
            tok = Token(TokenType.RPAREN, ")")
        elif self.ch == "{":
            tok = Token(TokenType.LBRACE, "{")
        elif self.ch == "}":
            tok = Token(TokenType.RBRACE, "}")
        elif self.ch == "!":
            if self.peek_char() == "=":
                self.read_char()
                tok = Token(TokenType.NOTEQ, "!=")
            else:
                tok = Token(TokenType.BANG, "!")
        elif self.ch == "-":
            tok = Token(TokenType.MINUS, "-")
        elif self.ch == "*":
            tok = Token(TokenType.STAR, "*")
        elif self.ch == "/":
            tok = Token(TokenType.SLASH, "/")
        elif self.ch == "<":
            tok = Token(TokenType.LESS, "<")
        elif self.ch == ">":
            tok = Token(TokenType.GREATER, ">")
        elif self.ch == "\0":
            tok = Token(TokenType.EOF, "")
        elif is_letter(self.ch):
            tok.literal = self.read_identifier()
            tok.type = tokens.lookup_ident(tok.literal)
            return tok
        elif is_digit(self.ch):
            tok.literal = self.read_number()
            tok.type = TokenType.NUM
            return tok

        self.read_char()
        return tok
