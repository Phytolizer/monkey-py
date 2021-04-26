from environment import Environment
from lexer import Lexer
from parser import Parser
import evaluator


def print_parser_errors(errs):
    for err in errs:
        print(f"parser error: {err}")


if __name__ == "__main__":
    env = Environment()
    while True:
        try:
            line = input(">> ")
        except EOFError:
            print()
            break

        l = Lexer(line)
        p = Parser(l)
        program = p.parse_program()
        if len(p.errors) > 0:
            print_parser_errors(p.errors)
            continue
        evaluated = evaluator.eval_node(program, env)
        if evaluated is not None:
            print(evaluated.inspect())
