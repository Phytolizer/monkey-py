from typing import List
import monkey_ast as ast
import monkey_code as code
import monkey_object as object
from dataclasses import dataclass


@dataclass(init=False)
class Compiler:
    _instructions: bytes
    _constants: List[object.Object]

    def __init__(self):
        self._instructions = bytes([])
        self._constants = []

    def _add_constant(self, obj: object.Object):
        self._constants.append(obj)
        return len(self._constants) - 1

    def _emit(self, op: code.Opcode, *operands):
        ins = code.make(op, *operands)
        pos = self._add_instruction(ins)
        return pos

    def _add_instruction(self, ins: List[int]):
        pos_new_instruction = len(self._instructions)
        l = list(self._instructions)
        l.extend(ins)
        self._instructions = bytes(l)

        return pos_new_instruction

    def compile(self, node):
        if isinstance(node, ast.Program):
            for s in node.statements:
                self.compile(s)
        elif isinstance(node, ast.ExpressionStatement):
            self.compile(node.expression)
            self._emit(code.Opcode.POP)
        elif isinstance(node, ast.InfixExpression):
            self.compile(node.left)
            self.compile(node.right)
            if node.operator == "+":
                self._emit(code.Opcode.ADD)
            elif node.operator == "-":
                self._emit(code.Opcode.SUB)
            elif node.operator == "*":
                self._emit(code.Opcode.MUL)
            elif node.operator == "/":
                self._emit(code.Opcode.DIV)
            else:
                raise RuntimeError(f"unknown operator {node.operator}")
        elif isinstance(node, ast.IntegerLiteral):
            integer = object.Integer(node.value)
            self._emit(code.Opcode.CONSTANT, self._add_constant(integer))

    def bytecode(self):
        return Bytecode(self._instructions, self._constants)


@dataclass(init=True, frozen=True)
class Bytecode:
    instructions: bytes
    constants: List[object.Object]
