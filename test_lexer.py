import pytest
from tokens import TokenType
from lexer import Lexer


class TestLexer:
    @pytest.fixture(scope="module")
    def next_token_lexer(self):
        return Lexer(
            """
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
        )

    @pytest.mark.parametrize(
        "kind,literal",
        (
            (TokenType.LET, "let"),
            (TokenType.IDENT, "five"),
            (TokenType.ASSIGN, "="),
            (TokenType.NUM, "5"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.LET, "let"),
            (TokenType.IDENT, "ten"),
            (TokenType.ASSIGN, "="),
            (TokenType.NUM, "10"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.LET, "let"),
            (TokenType.IDENT, "add"),
            (TokenType.ASSIGN, "="),
            (TokenType.FN, "fn"),
            (TokenType.LPAREN, "("),
            (TokenType.IDENT, "x"),
            (TokenType.COMMA, ","),
            (TokenType.IDENT, "y"),
            (TokenType.RPAREN, ")"),
            (TokenType.LBRACE, "{"),
            (TokenType.IDENT, "x"),
            (TokenType.PLUS, "+"),
            (TokenType.IDENT, "y"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.RBRACE, "}"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.LET, "let"),
            (TokenType.IDENT, "result"),
            (TokenType.ASSIGN, "="),
            (TokenType.IDENT, "add"),
            (TokenType.LPAREN, "("),
            (TokenType.IDENT, "five"),
            (TokenType.COMMA, ","),
            (TokenType.IDENT, "ten"),
            (TokenType.RPAREN, ")"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.BANG, "!"),
            (TokenType.MINUS, "-"),
            (TokenType.SLASH, "/"),
            (TokenType.STAR, "*"),
            (TokenType.NUM, "5"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.NUM, "5"),
            (TokenType.LESS, "<"),
            (TokenType.NUM, "10"),
            (TokenType.GREATER, ">"),
            (TokenType.NUM, "5"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.IF, "if"),
            (TokenType.LPAREN, "("),
            (TokenType.NUM, "5"),
            (TokenType.LESS, "<"),
            (TokenType.NUM, "10"),
            (TokenType.RPAREN, ")"),
            (TokenType.LBRACE, "{"),
            (TokenType.RETURN, "return"),
            (TokenType.TRUE, "true"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.RBRACE, "}"),
            (TokenType.ELSE, "else"),
            (TokenType.LBRACE, "{"),
            (TokenType.RETURN, "return"),
            (TokenType.FALSE, "false"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.RBRACE, "}"),
            (TokenType.NUM, "10"),
            (TokenType.EQ, "=="),
            (TokenType.NUM, "10"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.NUM, "10"),
            (TokenType.NOTEQ, "!="),
            (TokenType.NUM, "9"),
            (TokenType.SEMICOLON, ";"),
        ),
    )
    def test_next_token(self, kind, literal, next_token_lexer):
        tok = next_token_lexer.next_token()
        assert tok.type == kind
        assert tok.literal == literal
