from typing import List
from monkey_code import Instructions, Opcode, lookup, make, read_operands
import pytest


class TestCode:
    @pytest.mark.parametrize(
        "op,operands,expected",
        [
            (Opcode.CONSTANT, [0xFFFE], bytes([Opcode.CONSTANT, 0xFF, 0xFE])),
            (Opcode.ADD, [], bytes([Opcode.ADD])),
        ],
    )
    def test_make(self, op, operands, expected):
        instruction = make(op, *operands)
        assert len(instruction) == len(expected)
        for i, b in enumerate(expected):
            assert instruction[i] == b

    def test_instructions_string(self):
        instructions = Instructions(
            [
                make(Opcode.ADD),
                make(Opcode.CONSTANT, 2),
                make(Opcode.CONSTANT, 65535),
            ]
        )
        expected = """0000 OpAdd
0001 OpConstant 2
0004 OpConstant 65535
"""
        concatted = []
        for ins in instructions:
            concatted.extend(ins)
        concatted = Instructions(concatted)
        assert str(concatted) == expected

    @pytest.mark.parametrize(
        "op,operands,bytes_read",
        [
            (Opcode.CONSTANT, [65535], 2),
        ],
    )
    def test_read_operands(self, op: Opcode, operands: List[int], bytes_read: int):
        instruction = make(op, *operands)
        d = lookup(op)
        operands_read, n = read_operands(d, instruction[1:])
        assert n == bytes_read
        for op_read, want in zip(operands_read, operands):
            assert op_read == want
