import unittest
from tokens import TokenType, Token
import tokens

def is_letter(ch):
    return 'a' <= ch and ch <= 'z' or 'A' <= ch and ch <= 'Z' or ch == '_'

def is_whitespace(ch):
    return ch == ' ' or ch == '\t' or ch == '\r' or ch == '\n'

def is_digit(ch):
    return '0' <= ch and ch <= '9'

class Lexer:
    def __init__(self, source):
        self.input = source
        self.position = 0
        self.read_position = 0
        self.ch = '\0'

        self.read_char()
    
    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = '\0'
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self):
        if self.read_position >= len(self.input):
            return '\0'
        else:
            return self.input[self.read_position]

    def skip_whitespace(self):
        while is_whitespace(self.ch):
            self.read_char()

    def read_identifier(self):
        position = self.position
        while is_letter(self.ch):
            self.read_char()

        return self.input[position:self.position]

    def read_number(self):
        position = self.position
        while is_digit(self.ch):
            self.read_char()

        return self.input[position:self.position]
    
    def next_token(self):
        tok = Token(TokenType.Illegal, "")

        self.skip_whitespace()

        if self.ch == '=':
            if self.peek_char() == '=':
                self.read_char()
                tok = Token(TokenType.Eq, "==")
            else:
                tok = Token(TokenType.Assign, "=")
        elif self.ch == '+':
            tok = Token(TokenType.Plus, "+")
        elif self.ch == ',':
            tok = Token(TokenType.Comma, ",")
        elif self.ch == ';':
            tok = Token(TokenType.Semicolon, ";")
        elif self.ch == '(':
            tok = Token(TokenType.LParen, "(")
        elif self.ch == ')':
            tok = Token(TokenType.RParen, ")")
        elif self.ch == '{':
            tok = Token(TokenType.LBrace, "{")
        elif self.ch == '}':
            tok = Token(TokenType.RBrace, "}")
        elif self.ch == '!':
            if self.peek_char() == '=':
                self.read_char()
                tok = Token(TokenType.NotEq, "!=")
            else:
                tok = Token(TokenType.Bang, "!")
        elif self.ch == '-':
            tok = Token(TokenType.Minus, "-")
        elif self.ch == '*':
            tok = Token(TokenType.Star, "*")
        elif self.ch == '/':
            tok = Token(TokenType.Slash, "/")
        elif self.ch == '<':
            tok = Token(TokenType.Less, "<")
        elif self.ch == '>':
            tok = Token(TokenType.Greater, ">")
        elif self.ch == '\0':
            tok = Token(TokenType.Eof, "")
        elif is_letter(self.ch):
            tok.literal = self.read_identifier()
            tok.type = tokens.lookup_ident(tok.literal)
            return tok
        elif is_digit(self.ch):
            tok.literal = self.read_number()
            tok.type = TokenType.Num
            return tok

        self.read_char()
        return tok

class LexerTests(unittest.TestCase):
    def testNextToken(self):
        text = """
            let five = 5;
            let ten = 10;
            let add = fn(x, y) {
                x + y;
            };
            let result = add(five, ten);
            !-/*5;
            5 < 10 > 5;

            if (5 < 10) {
                return true;
            } else {
                return false;
            }

            10 == 10;
            10 != 9;
        """
        l = Lexer(text)
        tests = (
            (TokenType.Let, "let"),
            (TokenType.Ident, "five"),
            (TokenType.Assign, "="),
            (TokenType.Num, "5"),
            (TokenType.Semicolon, ";"),
            (TokenType.Let, "let"),
            (TokenType.Ident, "ten"),
            (TokenType.Assign, "="),
            (TokenType.Num, "10"),
            (TokenType.Semicolon, ";"),
            (TokenType.Let, "let"),
            (TokenType.Ident, "add"),
            (TokenType.Assign, "="),
            (TokenType.Fn, "fn"),
            (TokenType.LParen, "("),
            (TokenType.Ident, "x"),
            (TokenType.Comma, ","),
            (TokenType.Ident, "y"),
            (TokenType.RParen, ")"),
            (TokenType.LBrace, "{"),
            (TokenType.Ident, "x"),
            (TokenType.Plus, "+"),
            (TokenType.Ident, "y"),
            (TokenType.Semicolon, ";"),
            (TokenType.RBrace, "}"),
            (TokenType.Semicolon, ";"),
            (TokenType.Let, "let"),
            (TokenType.Ident, "result"),
            (TokenType.Assign, "="),
            (TokenType.Ident, "add"),
            (TokenType.LParen, "("),
            (TokenType.Ident, "five"),
            (TokenType.Comma, ","),
            (TokenType.Ident, "ten"),
            (TokenType.RParen, ")"),
            (TokenType.Semicolon, ";"),
            (TokenType.Bang, "!"),
            (TokenType.Minus, "-"),
            (TokenType.Slash, "/"),
            (TokenType.Star, "*"),
            (TokenType.Num, "5"),
            (TokenType.Semicolon, ";"),
            (TokenType.Num, "5"),
            (TokenType.Less, "<"),
            (TokenType.Num, "10"),
            (TokenType.Greater, ">"),
            (TokenType.Num, "5"),
            (TokenType.Semicolon, ";"),
            (TokenType.If, "if"),
            (TokenType.LParen, "("),
            (TokenType.Num, "5"),
            (TokenType.Less, "<"),
            (TokenType.Num, "10"),
            (TokenType.RParen, ")"),
            (TokenType.LBrace, "{"),
            (TokenType.Return, "return"),
            (TokenType.TRUE, "true"),
            (TokenType.Semicolon, ";"),
            (TokenType.RBrace, "}"),
            (TokenType.Else, "else"),
            (TokenType.LBrace, "{"),
            (TokenType.Return, "return"),
            (TokenType.FALSE, "false"),
            (TokenType.Semicolon, ";"),
            (TokenType.RBrace, "}"),
            (TokenType.Num, "10"),
            (TokenType.Eq, "=="),
            (TokenType.Num, "10"),
            (TokenType.Semicolon, ";"),
            (TokenType.Num, "10"),
            (TokenType.NotEq, "!="),
            (TokenType.Num, "9"),
            (TokenType.Semicolon, ";"),
        )

        for i, test in enumerate(tests):
            with self.subTest(i=i):
                tok = l.next_token()
                self.assertEqual(tok.type, test[0])
                self.assertEqual(tok.literal, test[1])

if __name__ == "__main__":
    unittest.main()
