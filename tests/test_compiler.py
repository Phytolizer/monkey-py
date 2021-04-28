from typing import Any, List
from monkey_compiler import Compiler
from lexer import Lexer
from monkey_parser import Parser
import monkey_code as code
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
        assert len(code.Instructions(actual)) == len(concatted)
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
                    code.make(code.Opcode.CONSTANT, 0),
                    code.make(code.Opcode.CONSTANT, 1),
                    code.make(code.Opcode.ADD),
                ],
            )
        ],
    )
    def test_integer_arithmetic(self, input, expected_constants, expected_instructions):
        self.run_compiler_test(input, expected_constants, expected_instructions)
