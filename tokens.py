from enum import Enum, auto


class TokenType(Enum):
    Illegal = auto()
    Eof = auto()

    Ident = auto()
    Num = auto()
    String = auto()

    Fn = auto()
    Let = auto()
    If = auto()
    Else = auto()
    Return = auto()
    TRUE = auto()
    FALSE = auto()

    Comma = auto()
    Semicolon = auto()

    Assign = auto()
    Plus = auto()
    Bang = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()

    Less = auto()
    Greater = auto()
    Eq = auto()
    NotEq = auto()

    LParen = auto()
    RParen = auto()
    LBrace = auto()
    RBrace = auto()
    LBracket = auto()
    RBracket = auto()


class Token:
    def __init__(self, type=TokenType.Illegal, literal=""):
        self.type = type
        self.literal = literal


KEYWORDS = {
    "fn": TokenType.Fn,
    "let": TokenType.Let,
    "if": TokenType.If,
    "else": TokenType.Else,
    "return": TokenType.Return,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


def lookup_ident(text):
    if text in KEYWORDS:
        return KEYWORDS[text]
    return TokenType.Ident
