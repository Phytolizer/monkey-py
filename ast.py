from abc import ABC, abstractmethod
import unittest

class Node(ABC):
    @abstractmethod
    def token_literal(self):
        pass

    @abstractmethod
    def string(self):
        pass

class Expression(Node):
    pass

class Statement(Node):
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements
    
    def token_literal(self):
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""
    
    def string(self):
        return "".join(map(lambda s: s.string(), self.statements))

class LetStatement(Statement):
    def __init__(self, token, name, value):
        self.token = token
        self.name = name
        self.value = value
    
    def token_literal(self):
        return self.token.literal
    
    def string(self):
        out = f"{self.token_literal()} {self.name.string()}"
        if self.value is not None:
            out += f" = {self.value.string()}"
        return f"{out};"

class Identifier(Expression):
    def __init__(self, token, value):
        self.token = token
        self.value = value
    
    def token_literal(self):
        return self.token.literal
    
    def string(self):
        return self.token_literal()

class IntegerLiteral(Expression):
    def __init__(self, token, value):
        self.token = token
        self.value = value
    
    def token_literal(self):
        return self.token.literal
    
    def string(self):
        return self.token_literal()

class ReturnStatement(Statement):
    def __init__(self, token, return_value):
        self.token = token
        self.return_value = return_value
    
    def token_literal(self):
        return self.token.literal
    
    def string(self):
        return f"{self.token_literal()} {self.return_value};"
    
class ExpressionStatement(Statement):
    def __init__(self, token, expression):
        self.token = token
        self.expression = expression

    def token_literal(self):
        return self.token.literal
    
    def string(self):
        return self.expression.string()

class AstTests(unittest.TestCase):
    def test_string(self):
        program = Program([
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
        ])

        self.assertEqual(program.string(), "let myVar = anotherVar;")

if __name__ == "__main__":
    from tokens import Token, TokenType
    unittest.main()
