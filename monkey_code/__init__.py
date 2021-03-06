import struct
from typing import List
from enum import IntEnum, auto
from dataclasses import dataclass
from struct import pack


class Opcode(IntEnum):
    CONSTANT = auto()

    TRUE = auto()
    FALSE = auto()
    NULL = auto()

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()

    MINUS = auto()
    BANG = auto()

    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_THAN = auto()

    POP = auto()

    JUMP_NOT_TRUTHY = auto()
    JUMP = auto()

    GET_GLOBAL = auto()
    SET_GLOBAL = auto()


@dataclass
class Definition:
    name: str
    operand_widths: List[int]


class Instructions:
    def __init__(self, b: bytearray):
        self.b = b

    def __str__(self):
        out = ""
        i = 0
        while i < len(self):
            try:
                d = lookup(self.b[i])
            except KeyError as e:
                out += f"ERROR: {e}\n"
                continue
            operands, read = read_operands(d, self.b[i + 1 :])
            out += f"{i:04} {self.fmt_instruction(d, operands)}\n"
            i += 1 + read
        return out

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.b)

    def __index__(self, i):
        return self.b[i]

    def __len__(self):
        return len(self.b)

    def fmt_instruction(self, d: Definition, operands: List[int]):
        operand_count = len(d.operand_widths)
        if len(operands) != operand_count:
            return f"ERROR: operand len {len(operands)} does not match defined {operand_count}\n"
        if operand_count == 0:
            return d.name
        elif operand_count == 1:
            return f"{d.name} {operands[0]}"
        return f"ERROR: unhandled operand_count for {d.name}\n"


_definitions = {
    Opcode.CONSTANT: Definition("OpConstant", [2]),
    Opcode.TRUE: Definition("OpTrue", []),
    Opcode.FALSE: Definition("OpFalse", []),
    Opcode.NULL: Definition("OpNull", []),
    Opcode.ADD: Definition("OpAdd", []),
    Opcode.SUB: Definition("OpSub", []),
    Opcode.MUL: Definition("OpMul", []),
    Opcode.DIV: Definition("OpDiv", []),
    Opcode.MINUS: Definition("OpMinus", []),
    Opcode.BANG: Definition("OpBang", []),
    Opcode.EQUAL: Definition("OpEqual", []),
    Opcode.NOT_EQUAL: Definition("OpNotEqual", []),
    Opcode.GREATER_THAN: Definition("OpGreaterThan", []),
    Opcode.POP: Definition("OpPop", []),
    Opcode.JUMP_NOT_TRUTHY: Definition("OpJumpNotTruthy", [2]),
    Opcode.JUMP: Definition("OpJump", [2]),
    Opcode.GET_GLOBAL: Definition("OpGetGlobal", [2]),
    Opcode.SET_GLOBAL: Definition("OpSetGlobal", [2]),
}


def lookup(op: int):
    "Note: this throws a KeyError on unknown input."
    return _definitions[Opcode(op)]


def make(op: Opcode, *operands):
    try:
        d = _definitions[op]
    except KeyError:
        return bytearray([])

    instruction_len = 1 + sum(d.operand_widths)
    instruction = list(0x00 for _ in range(instruction_len))
    instruction[0] = op
    offset = 1
    for w, o in zip(d.operand_widths, operands):
        if w == 2:
            instruction[offset : offset + 2] = pack(">H", o)
        offset += w
    return bytearray(instruction)


def read_operands(d: Definition, ins: Instructions):
    operands = [None for _ in range(len(d.operand_widths))]
    offset = 0
    for i, width in enumerate(d.operand_widths):
        if width == 2:
            operands[i] = read_uint16(bytearray(ins[offset : offset + 2]))
        offset += width
    return operands, offset


def read_uint16(ins: bytearray):
    return struct.unpack(">H", ins)[0]
