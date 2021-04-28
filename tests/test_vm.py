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


def check_boolean_object(expected: bool, actual: object.Object):
    assert isinstance(actual, object.Boolean)
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
    if isinstance(expected, bool):
        check_boolean_object(expected, actual)
    elif isinstance(expected, int):
        check_integer_object(expected, actual)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("1", 1),
        ("2", 2),
        ("1 + 2", 3),
        ("1 - 2", -1),
        ("1 * 2", 2),
        ("4 / 2", 2),
        ("50 / 2 * 2 + 10 - 5", 55),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("5 * (2 + 10)", 60),
    ],
)
def test_integer_arithmetic(input: str, expected: int):
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
    ],
)
def test_boolean_expression(input: str, expected: bool):
    run_vm_test(input, expected)
