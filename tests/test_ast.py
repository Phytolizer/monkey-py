from monkey_ast import Program, LetStatement, Identifier
from tokens import Token, TokenType


class TestAst:
    def test_string(self):
        program = Program(
            [
                LetStatement(
                    Token(TokenType.Let, "let"),
                    Identifier(
                        Token(TokenType.Ident, "myVar"),
                        "myVar",
                    ),
                    Identifier(
                        Token(TokenType.Ident, "anotherVar"),
                        "anotherVar",
                    ),
                )
            ]
        )

        assert program.string() == "let myVar = anotherVar;"
