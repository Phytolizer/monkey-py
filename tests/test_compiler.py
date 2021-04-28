from typing import Any, List
from monkey_compiler import Compiler
from lexer import Lexer
from monkey_parser import Parser
import monkey_code as code
from monkey_code import Opcode
import monkey_object as object
import pytest


class TestCompiler:
    def parse(self, input: str):
        l = Lexer(input)
        p = Parser(l)
        return p.parse_program()

    def check_integer_object(self, expected: int, actual: object.Object):
        assert isinstance(actual, object.Integer)
        assert actual.value == expected

    def check_constants(self, expected: List[Any], actual: List[object.Object]):
        assert len(expected) == len(actual)
        for act, constant in zip(actual, expected):
            if isinstance(constant, int):
                self.check_integer_object(constant, act)

    def check_instructions(
        self, expected: List[code.Instructions], actual: code.Instructions
    ):
        concatted = self.concat_instructions(expected)
        assert str(code.Instructions(actual)) == str(concatted)
        for a, ins in zip(actual, concatted):
            assert a == ins

    def concat_instructions(self, instructions: code.Instructions):
        out = []
        for ins in instructions:
            out.extend(ins)
        return code.Instructions(out)

    def run_compiler_test(self, input, expected_constants, expected_instructions):
        program = self.parse(input)
        compiler = Compiler()
        compiler.compile(program)
        bytecode = compiler.bytecode()
        self.check_instructions(expected_instructions, bytecode.instructions)
        self.check_constants(expected_constants, bytecode.constants)

    @pytest.mark.parametrize(
        "input,expected_constants,expected_instructions",
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
    def test_integer_arithmetic(self, input, expected_constants, expected_instructions):
        self.run_compiler_test(input, expected_constants, expected_instructions)

    @pytest.mark.parametrize(
        "input,expected_constants,expected_instructions",
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
    def test_boolean_expression(self, input, expected_constants, expected_instructions):
        self.run_compiler_test(input, expected_constants, expected_instructions)

    @pytest.mark.parametrize(
        "input,expected_constants,expected_instructions",
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
    def test_conditionals(self, input, expected_constants, expected_instructions):
        self.run_compiler_test(input, expected_constants, expected_instructions)
