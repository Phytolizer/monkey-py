from lexer import Lexer
from tokens import TokenType
import pytest


class TestLexer:
    @pytest.fixture(scope="class")
    def lexer(self):
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
            "foobar"
            "foo bar"
            [1, 2];
            {"foo": "bar"}
        """
        return Lexer(text)

    @pytest.mark.parametrize(
        "token_type,token_name",
        [
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
            (TokenType.String, "foobar"),
            (TokenType.String, "foo bar"),
            (TokenType.LBracket, "["),
            (TokenType.Num, "1"),
            (TokenType.Comma, ","),
            (TokenType.Num, "2"),
            (TokenType.RBracket, "]"),
            (TokenType.Semicolon, ";"),
            (TokenType.LBrace, "{"),
            (TokenType.String, "foo"),
            (TokenType.Colon, ":"),
            (TokenType.String, "bar"),
            (TokenType.RBrace, "}"),
            (TokenType.Eof, ""),
        ],
    )
    def test_next_token(self, lexer, token_type, token_name):
        tok = lexer.next_token()
        assert tok.type == token_type
        assert tok.literal == token_name
