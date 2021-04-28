from monkey_vm import VM
from typing import Any
import monkey_ast as ast
import lexer
import monkey_object as object
import monkey_parser as parser
import monkey_compiler as compiler
import pytest


def parse(input: str):
    l = lexer.Lexer(input)
    p = parser.Parser(l)
    return p.parse_program()


def check_integer_object(expected: int, actual: object.Object):
    assert isinstance(actual, object.Integer)
    assert actual.value == expected


def run_vm_test(input: str, expected: Any):
    program = parse(input)
    comp = compiler.Compiler()
    comp.compile(program)
    vm = VM(comp.bytecode())
    vm.run()
    stack_elem = vm.last_popped_stack_elem()
    check_expected_object(expected, stack_elem)


def check_expected_object(expected: Any, actual: object.Object):
    if isinstance(expected, int):
        check_integer_object(expected, actual)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("1", 1),
        ("2", 2),
        ("1 + 2", 3),
    ],
)
def test_integer_arithmetic(input, expected):
    run_vm_test(input, expected)
