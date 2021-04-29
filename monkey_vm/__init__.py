from dataclasses import dataclass
from monkey_compiler import Bytecode
from typing import List
import monkey_object as object
import monkey_code as code

STACK_SIZE = 2048
TRUE = object.Boolean(True)
FALSE = object.Boolean(False)
NULL = object.Null()


def native_bool_to_boolean_object(b):
    if b:
        return TRUE
    return FALSE


def is_truthy(obj: object.Object):
    if isinstance(obj, object.Boolean):
        return obj.value
    elif obj == NULL:
        return False
    else:
        return True


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
        self.push(object.Integer(result))

    def execute_binary_operation(self, op: code.Opcode):
        right = self.pop()
        left = self.pop()
        if (
            left.type() == object.ObjectType.INTEGER
            and right.type() == object.ObjectType.INTEGER
        ):
            self.execute_binary_integer_operation(op, left, right)
            return

        raise RuntimeError(
            f"unsupported types for binary operation: {left.type()}, {right.type()}"
        )

    def execute_integer_comparison(
        self, op: code.Opcode, left: object.Object, right: object.Object
    ):
        if op == code.Opcode.EQUAL:
            self.push(native_bool_to_boolean_object(right.value == left.value))
        elif op == code.Opcode.NOT_EQUAL:
            self.push(native_bool_to_boolean_object(right.value != left.value))
        elif op == code.Opcode.GREATER_THAN:
            self.push(native_bool_to_boolean_object(left.value > right.value))
        else:
            raise RuntimeError(f"unknown operator: {op}")

    def execute_comparison(self, op: code.Opcode):
        right = self.pop()
        left = self.pop()
        if (
            left.type() == object.ObjectType.INTEGER
            and right.type() == object.ObjectType.INTEGER
        ):
            self.execute_integer_comparison(op, left, right)
        elif op == code.Opcode.EQUAL:
            self.push(native_bool_to_boolean_object(right == left))
        elif op == code.Opcode.NOT_EQUAL:
            self.push(native_bool_to_boolean_object(right != left))
        else:
            raise RuntimeError(f"unknown operator: {op} ({left.type()} {right.type()})")

    def execute_bang_operator(self):
        operand = self.pop()
        if operand == FALSE or operand == NULL:
            self.push(TRUE)
        else:
            self.push(FALSE)

    def execute_minus_operator(self):
        operand = self.pop()
        if operand.type() == object.ObjectType.INTEGER:
            self.push(object.Integer(-operand.value))
        else:
            raise RuntimeError(f"unsupported type for negation: {operand.type()}")

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
            elif op == code.Opcode.TRUE:
                self.push(TRUE)
            elif op == code.Opcode.FALSE:
                self.push(FALSE)
            elif op in (
                code.Opcode.ADD,
                code.Opcode.SUB,
                code.Opcode.MUL,
                code.Opcode.DIV,
            ):
                self.execute_binary_operation(op)
            elif op in (
                code.Opcode.EQUAL,
                code.Opcode.NOT_EQUAL,
                code.Opcode.GREATER_THAN,
            ):
                self.execute_comparison(op)
            elif op == code.Opcode.BANG:
                self.execute_bang_operator()
            elif op == code.Opcode.MINUS:
                self.execute_minus_operator()
            elif op == code.Opcode.POP:
                self.pop()
            elif op == code.Opcode.JUMP:
                pos = code.read_uint16(self._instructions[ip + 1 : ip + 3])
                ip = pos - 1
            elif op == code.Opcode.JUMP_NOT_TRUTHY:
                pos = code.read_uint16(self._instructions[ip + 1 : ip + 3])
                ip += 2
                condition = self.pop()
                if not is_truthy(condition):
                    ip = pos - 1
            elif op == code.Opcode.NULL:
                self.push(NULL)
            ip += 1

        return None
