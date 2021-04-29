from typing import Any, List
from monkey_compiler import Compiler, Symbol, SymbolScope, SymbolTable
from lexer import Lexer
from monkey_parser import Parser
import monkey_code as code
from monkey_code import Opcode
import monkey_object
import pytest


def concat_instructions(instructions: List[code.Instructions]):
    out = []
    for ins in instructions:
        out.extend(ins)
    return code.Instructions(bytearray(out))


def parse(text: str):
    lex = Lexer(text)
    par = Parser(lex)
    return par.parse_program()


def check_integer_object(expected: int, actual: monkey_object.Object):
    assert isinstance(actual, monkey_object.Integer)
    assert actual.value == expected


def check_constants(expected: List[Any], actual: List[monkey_object.Object]):
    assert len(expected) == len(actual)
    for act, constant in zip(actual, expected):
        if isinstance(constant, int):
            check_integer_object(constant, act)


def check_instructions(
        expected: List[code.Instructions], actual: bytearray
):
    concatted = concat_instructions(expected)
    assert str(code.Instructions(actual)) == str(concatted)
    for a, ins in zip(actual, concatted):
        assert a == ins


def run_compiler_test(text, expected_constants, expected_instructions):
    program = parse(text)
    compiler = Compiler()
    compiler.compile(program)
    bytecode = compiler.bytecode()
    check_instructions(expected_instructions, bytecode.instructions)
    check_constants(expected_constants, bytecode.constants)


class TestCompiler:

    @pytest.mark.parametrize(
        "text,expected_constants,expected_instructions",
        [
            (
                "1 + 2",
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.ADD),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "1; 2",
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "1 - 2",
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.SUB),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "1 * 2",
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.MUL),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "2 / 1",
                [2, 1],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.DIV),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "-1",
                [1],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.MINUS),
                    code.make(Opcode.POP),
                ],
            ),
        ],
    )
    def test_integer_arithmetic(self, text, expected_constants, expected_instructions):
        run_compiler_test(text, expected_constants, expected_instructions)

    @pytest.mark.parametrize(
        "text,expected_constants,expected_instructions",
        [
            (
                "true",
                [],
                [
                    code.make(Opcode.TRUE),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "false",
                [],
                [
                    code.make(Opcode.FALSE),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "1 > 2",
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.GREATER_THAN),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "1 < 2",
                [2, 1],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.GREATER_THAN),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "1 == 2",
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.EQUAL),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "1 != 2",
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.NOT_EQUAL),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "true == false",
                [],
                [
                    code.make(Opcode.TRUE),
                    code.make(Opcode.FALSE),
                    code.make(Opcode.EQUAL),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "true != false",
                [],
                [
                    code.make(Opcode.TRUE),
                    code.make(Opcode.FALSE),
                    code.make(Opcode.NOT_EQUAL),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "!true",
                [],
                [
                    code.make(Opcode.TRUE),
                    code.make(Opcode.BANG),
                    code.make(Opcode.POP),
                ],
            ),
        ],
    )
    def test_boolean_expression(self, text, expected_constants, expected_instructions):
        run_compiler_test(text, expected_constants, expected_instructions)

    @pytest.mark.parametrize(
        "text,expected_constants,expected_instructions",
        [
            (
                "if (true) { 10 }; 3333;",
                [10, 3333],
                [
                    code.make(Opcode.TRUE),
                    code.make(Opcode.JUMP_NOT_TRUTHY, 10),
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.JUMP, 11),
                    code.make(Opcode.NULL),
                    code.make(Opcode.POP),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.POP),
                ],
            ),
            (
                "if (true) { 10 } else { 20 }; 3333;",
                [10, 20, 3333],
                [
                    code.make(Opcode.TRUE),
                    code.make(Opcode.JUMP_NOT_TRUTHY, 10),
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.JUMP, 13),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.POP),
                    code.make(Opcode.CONSTANT, 2),
                    code.make(Opcode.POP),
                ],
            ),
        ],
    )
    def test_conditionals(self, text, expected_constants, expected_instructions):
        run_compiler_test(text, expected_constants, expected_instructions)

    @pytest.mark.parametrize(
        "text,expected_constants,expected_instructions",
        [
            (
                """
                let one = 1;
                let two = 2;
                """,
                [1, 2],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SET_GLOBAL, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.SET_GLOBAL, 1),
                ],
            ),
            (
                """
                let one = 1;
                one;
                """,
                [1],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SET_GLOBAL, 0),
                    code.make(Opcode.GET_GLOBAL, 0),
                    code.make(Opcode.POP),
                ],
            ),
            (
                """
                let one = 1;
                let two = one;
                two;
                """,
                [1],
                [
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SET_GLOBAL, 0),
                    code.make(Opcode.GET_GLOBAL, 0),
                    code.make(Opcode.SET_GLOBAL, 1),
                    code.make(Opcode.GET_GLOBAL, 1),
                    code.make(Opcode.POP),
                ],
            ),
        ],
    )
    def test_global_let_statements(
        self, text, expected_constants, expected_instructions
    ):
        run_compiler_test(text, expected_constants, expected_instructions)

    def test_define(self):
        expected = {
            "a": Symbol("a", SymbolScope.GLOBAL, 0),
            "b": Symbol("b", SymbolScope.GLOBAL, 1),
        }

        glob = SymbolTable()
        a = glob.define("a")
        assert a == expected["a"]

        b = glob.define("b")
        assert b == expected["b"]

    def test_resolve_global(self):
        glob = SymbolTable()
        glob.define("a")
        glob.define("b")
        expected = [
            Symbol("a", SymbolScope.GLOBAL, 0),
            Symbol("b", SymbolScope.GLOBAL, 1),
        ]
        for sym in expected:
            result = glob.resolve(sym.name)
            assert result == sym
