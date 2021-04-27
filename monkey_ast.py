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


class Boolean(Expression):
    def __init__(self, token, value):
        self.token = token
        self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token_literal()


class PrefixExpression(Expression):
    def __init__(self, token, operator, right):
        self.token = token
        self.operator = operator
        self.right = right

    def token_literal(self):
        return self.token.literal

    def string(self):
        return f"({self.operator}{self.right.string()})"


class InfixExpression(Expression):
    def __init__(self, token, left, operator, right):
        self.token = token
        self.left = left
        self.operator = operator
        self.right = right

    def token_literal(self):
        return self.token.literal

    def string(self):
        return f"({self.left.string()} {self.operator} {self.right.string()})"


class FunctionLiteral(Expression):
    def __init__(self, token, parameters, body):
        self.token = token
        self.parameters = parameters
        self.body = body

    def token_literal(self):
        return self.token.literal

    def string(self):
        params = ", ".join(map(lambda p: p.string(), self.parameters))
        return f"{self.token_literal()}({params}) {self.body.string()}"


class IfExpression(Expression):
    def __init__(self, token, condition, consequence, alternative):
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = f"{self.token_literal()}{self.condition.string()} {self.consequence.string()}"
        if self.alternative is not None:
            out += f" else {self.alternative.string()}"
        return out


class CallExpression(Expression):
    def __init__(self, token, function, arguments):
        self.token = token
        self.function = function
        self.arguments = arguments

    def token_literal(self):
        return self.token.literal

    def string(self):
        args = ", ".join(map(lambda a: a.string(), self.arguments))
        return f"{self.function.string()}({args})"


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


class BlockStatement(Statement):
    def __init__(self, token, statements):
        self.token = token
        self.statements = statements

    def token_literal(self):
        return self.token.literal

    def string(self):
        return "".join(map(lambda s: s.string(), self.statements))


class StringLiteral(Expression):
    def __init__(self, token, value):
        self.token = token
        self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.value


class ArrayLiteral(Expression):
    def __init__(self, token, elements):
        self.token = token
        self.elements = elements

    def token_literal(self):
        return self.token.literal

    def string(self):
        return f"[{', '.join(map(lambda s: s.string(), self.elements))}]"


class IndexExpression(Expression):
    def __init__(self, token, left, index):
        self.token = token
        self.left = left
        self.index = index

    def token_literal(self):
        return self.token.literal

    def string(self):
        return f"({self.left.string()}[{self.index.string()}])"


class HashLiteral(Expression):
    def __init__(self, token, pairs):
        self.token = token
        self.pairs = pairs

    def token_literal(self):
        return self.token.literal

    def string(self):
        pairs = []
        for key, value in self.pairs:
            pairs.append(f"{key.string()}:{value.string()}")
        return f"{{{', '.join(pairs)}}}"
