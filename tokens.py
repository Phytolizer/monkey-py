from enum import Enum, auto


class TokenType(Enum):
    ILLEGAL = auto()
    EOF = auto()

    IDENT = auto()
    NUM = auto()

    FN = auto()
    LET = auto()
    IF = auto()
    ELSE = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()

    COMMA = auto()
    SEMICOLON = auto()

    ASSIGN = auto()
    PLUS = auto()
    BANG = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    LESS = auto()
    GREATER = auto()
    EQ = auto()
    NOTEQ = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()


class Token:
    def __init__(self, type, literal):
        self.type = type
        self.literal = literal


KEYWORDS = {
    "fn": TokenType.FN,
    "let": TokenType.LET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


def lookup_ident(text):
    if text in KEYWORDS:
        return KEYWORDS[text]
    return TokenType.IDENT
