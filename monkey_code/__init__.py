from typing import List
from enum import IntEnum
from dataclasses import dataclass
from struct import pack


class Opcode(IntEnum):
    CONSTANT = 0


@dataclass
class Definition:
    name: str
    operand_widths: List[int]


_definitions = {
    Opcode.CONSTANT: Definition("OpConstant", [2]),
}


def lookup(op: int):
    "Note: this throws a KeyError on unknown input."
    return _definitions[Opcode(op)]


def make(op: Opcode, operands: List[int]):
    try:
        d = _definitions[op]
    except KeyError:
        return bytes([])

    instruction_len = 1 + sum(d.operand_widths)
    instruction = list(0x00 for _ in range(instruction_len))
    instruction[0] = op
    offset = 1
    for w, o in zip(d.operand_widths, operands):
        if w == 2:
            instruction[offset : offset + 2] = pack(">H", o)
        offset += w
    return bytes(instruction)
