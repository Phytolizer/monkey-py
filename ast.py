from abc import ABC, abstractmethod

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
        return self.statements.join("")

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
            out += f" {self.value.string()}"
        return f"{out};"

class Identifier(Expression):
    def __init__(self, token, value):
        self.token = token
        self.value = value
    
    def token_literal(self):
        return self.token.literal
    
    def string(self):
        return self.token_literal()
