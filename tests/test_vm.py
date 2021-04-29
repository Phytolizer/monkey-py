from monkey_vm import NULL, VM
from typing import Any
import lexer
import monkey_object
import monkey_parser as parser
import monkey_compiler as compiler
import pytest


def parse(text: str):
    lex = lexer.Lexer(text)
    par = parser.Parser(lex)
    return par.parse_program()


def check_integer_object(expected: int, actual: monkey_object.Object):
    assert isinstance(actual, monkey_object.Integer)
    assert actual.value == expected


def check_boolean_object(expected: bool, actual: monkey_object.Object):
    assert isinstance(actual, monkey_object.Boolean)
    assert actual.value == expected


def run_vm_test(text: str, expected: Any):
    program = parse(text)
    comp = compiler.Compiler()
    comp.compile(program)
    vm = VM(comp.bytecode())
    vm.run()
    stack_elem = vm.last_popped_stack_elem()
    check_expected_object(expected, stack_elem)


def check_expected_object(expected: Any, actual: monkey_object.Object):
    if isinstance(expected, bool):
        check_boolean_object(expected, actual)
    elif isinstance(expected, int):
        check_integer_object(expected, actual)
    elif isinstance(expected, monkey_object.Null):
        assert actual == NULL


@pytest.mark.parametrize(
    "text,expected",
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
        ("-5", -5),
        ("-10", -10),
        ("-50 + 100 + -50", 0),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ],
)
def test_integer_arithmetic(text: str, expected: int):
    run_vm_test(text, expected)


@pytest.mark.parametrize(
    "text,expected",
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
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
        ("!(if (false) { 5; })", True),
    ],
)
def test_boolean_expression(text: str, expected: bool):
    run_vm_test(text, expected)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("if (true) { 10 }", 10),
        ("if (true) { 10 } else { 20 }", 10),
        ("if (false) { 10 } else { 20 } ", 20),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 < 2) { 10 } else { 20 }", 10),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 > 2) { 10 }", NULL),
        ("if (false) { 10 }", NULL),
        ("if ((if (false) { 10 })) { 10 } else { 20 }", 20),
    ],
)
def test_conditionals(text: str, expected: int):
    run_vm_test(text, expected)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("let one = 1; one", 1),
        ("let one = 1; let two = 2; one + two", 3),
        ("let one = 1; let two = one + one; one + two", 3),
    ]
)
def test_global_let_statements(text: str, expected: int):
    run_vm_test(text, expected)
