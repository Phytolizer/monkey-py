from dataclasses import dataclass
from monkey_compiler import Bytecode
from typing import List
import monkey_object as object
import monkey_code as code

STACK_SIZE = 2048


@dataclass
class VM:
    _constants: List[object.Object]
    _instructions: code.Instructions
    _stack: List[object.Object]
    _sp: int

    def __init__(self, bytecode: Bytecode):
        self._instructions = bytecode.instructions
        self._constants = bytecode.constants
        self._stack = [None for _ in range(STACK_SIZE)]
        self._sp = 0

    def stack_top(self):
        if self._sp == 0:
            return None
        return self._stack[self._sp - 1]

    def push(self, o: object.Object):
        if self._sp >= STACK_SIZE:
            raise RuntimeError("stack overflow")
        self._stack[self._sp] = o
        self._sp += 1

    def pop(self):
        o = self._stack[self._sp - 1]
        self._sp -= 1
        return o

    def last_popped_stack_elem(self):
        return self._stack[self._sp]

    def execute_binary_integer_operation(
        self, op: code.Opcode, left: object.Object, right: object.Object
    ):
        result = None
        if op == code.Opcode.ADD:
            result = left.value + right.value
        elif op == code.Opcode.SUB:
            result = left.value - right.value
        elif op == code.Opcode.MUL:
            result = left.value * right.value
        elif op == code.Opcode.DIV:
            result = left.value // right.value
        else:
            raise RuntimeError(f"unknown integer operator: {op}")
        return self.push(object.Integer(result))

    def execute_binary_operation(self, op: code.Opcode):
        right = self.pop()
        left = self.pop()
        if (
            left.type() == object.ObjectType.INTEGER
            and right.type() == object.ObjectType.INTEGER
        ):
            return self.execute_binary_integer_operation(op, left, right)

        raise RuntimeError(
            f"unsupported types for binary operation: {left.type()}, {right.type()}"
        )

    def run(self):
        ip = 0
        while ip < len(self._instructions):
            op = code.Opcode(self._instructions[ip])
            if op == code.Opcode.CONSTANT:
                const_index = code.read_uint16(
                    bytes(self._instructions[ip + 1 : ip + 3])
                )
                ip += 2
                self.push(self._constants[const_index])
            elif op in (
                code.Opcode.ADD,
                code.Opcode.SUB,
                code.Opcode.MUL,
                code.Opcode.DIV,
            ):
                self.execute_binary_operation(op)
            elif op == code.Opcode.POP:
                self.pop()
            ip += 1

        return None
