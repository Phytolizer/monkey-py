from lexer import Lexer
from tokens import TokenType

if __name__ == "__main__":
    while True:
        try:
            line = input(">> ")
        except EOFError:
            print()
            break

        l = Lexer(line)

        while True:
            tok = l.next_token()
            if tok.type == TokenType.Eof:
                break
            print(f"{{Type:{tok.type} Literal:{tok.literal}}}")
