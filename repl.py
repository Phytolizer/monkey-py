from monkey_vm import VM
from monkey_compiler import Compiler
from environment import Environment
from lexer import Lexer
from monkey_parser import Parser
import evaluator


def print_parser_errors(errs):
    for err in errs:
        print(f"parser error: {err}")


if __name__ == "__main__":
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
        comp = Compiler()
        try:
            comp.compile(program)
        except RuntimeError as e:
            print(f"compilation failed: {e}")
            continue
        machine = VM(comp.bytecode())
        try:
            machine.run()
        except RuntimeError as e:
            print(f"executing bytecode failed: {e}")
            continue
        stack_top = machine.stack_top()
        print(stack_top.inspect())
