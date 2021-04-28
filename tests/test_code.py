from monkey_code import Definition, Opcode, make
import pytest


class TestCode:
    @pytest.mark.parametrize(
        "op,operands,expected",
        [(Opcode.CONSTANT, [0xFFFE], bytes([Opcode.CONSTANT, 0xFF, 0xFE]))],
    )
    def test_make(self, op, operands, expected):
        instruction = make(op, operands)
        assert len(instruction) == len(expected)
        for i, b in enumerate(expected):
            assert instruction[i] == b
