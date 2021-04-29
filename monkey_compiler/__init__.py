from typing import List
import monkey_ast as ast
import monkey_code as code
import monkey_object as object
from monkey_code import Opcode
from dataclasses import dataclass


@dataclass
class EmittedInstruction:
    opcode: Opcode
    position: int


@dataclass(init=False)
class Compiler:
    _instructions: bytearray
    _constants: List[object.Object]
    _last_instruction: EmittedInstruction
    _previous_instruction: EmittedInstruction

    def __init__(self):
        self._instructions = bytearray([])
        self._constants = []
        self._last_instruction = EmittedInstruction(0, 0)
        self._previous_instruction = EmittedInstruction(0, 0)

    def _add_constant(self, obj: object.Object):
        self._constants.append(obj)
        return len(self._constants) - 1

    def _set_last_instruction(self, op: Opcode, pos: int):
        previous = self._last_instruction
        last = EmittedInstruction(op, pos)
        self._previous_instruction = previous
        self._last_instruction = last

    def _emit(self, op: Opcode, *operands):
        ins = code.make(op, *operands)
        pos = self._add_instruction(ins)

        self._set_last_instruction(op, pos)

        return pos

    def _add_instruction(self, ins: List[int]):
        pos_new_instruction = len(self._instructions)
        ins_lst = list(self._instructions)
        ins_lst.extend(ins)
        self._instructions = bytearray(ins_lst)

        return pos_new_instruction

    def _last_instruction_is_pop(self):
        return self._last_instruction.opcode == Opcode.POP

    def _remove_last_pop(self):
        self._instructions = self._instructions[: self._last_instruction.position]
        self._last_instruction = self._previous_instruction

    def _replace_instruction(self, pos: int, new_instruction: bytearray):
        self._instructions[pos : pos + len(new_instruction)] = new_instruction

    def _change_operand(self, op_pos: int, operand: int):
        op = Opcode(self._instructions[op_pos])
        new_instruction = code.make(op, operand)
        self._replace_instruction(op_pos, new_instruction)

    def compile(self, node):
        if isinstance(node, ast.Program):
            for s in node.statements:
                self.compile(s)
        elif isinstance(node, ast.BlockStatement):
            for s in node.statements:
                self.compile(s)
        elif isinstance(node, ast.ExpressionStatement):
            self.compile(node.expression)
            self._emit(Opcode.POP)
        elif isinstance(node, ast.IfExpression):
            self.compile(node.condition)
            # this jump offset is bogus.
            jump_not_truthy_pos = self._emit(Opcode.JUMP_NOT_TRUTHY, 9999)
            self.compile(node.consequence)
            if self._last_instruction_is_pop():
                self._remove_last_pop()
            jump_pos = self._emit(Opcode.JUMP, 9999)
            after_consequence_pos = len(self._instructions)
            self._change_operand(jump_not_truthy_pos, after_consequence_pos)
            if node.alternative is None:
                self._emit(Opcode.NULL)
            else:
                self.compile(node.alternative)
                if self._last_instruction_is_pop():
                    self._remove_last_pop()
            after_alternative_pos = len(self._instructions)
            self._change_operand(jump_pos, after_alternative_pos)
        elif isinstance(node, ast.InfixExpression):
            if node.operator == "<":
                self.compile(node.right)
                self.compile(node.left)
                self._emit(Opcode.GREATER_THAN)
                return
            self.compile(node.left)
            self.compile(node.right)
            if node.operator == "+":
                self._emit(Opcode.ADD)
            elif node.operator == "-":
                self._emit(Opcode.SUB)
            elif node.operator == "*":
                self._emit(Opcode.MUL)
            elif node.operator == "/":
                self._emit(Opcode.DIV)
            elif node.operator == ">":
                self._emit(Opcode.GREATER_THAN)
            elif node.operator == "==":
                self._emit(Opcode.EQUAL)
            elif node.operator == "!=":
                self._emit(Opcode.NOT_EQUAL)
            else:
                raise RuntimeError(f"unknown operator {node.operator}")
        elif isinstance(node, ast.PrefixExpression):
            self.compile(node.right)
            if node.operator == "!":
                self._emit(Opcode.BANG)
            elif node.operator == "-":
                self._emit(Opcode.MINUS)
            else:
                raise RuntimeError(f"unknown operator {node.operator}")
        elif isinstance(node, ast.IntegerLiteral):
            integer = object.Integer(node.value)
            self._emit(Opcode.CONSTANT, self._add_constant(integer))
        elif isinstance(node, ast.Boolean):
            if node.value:
                self._emit(Opcode.TRUE)
            else:
                self._emit(Opcode.FALSE)

    def bytecode(self):
        return Bytecode(bytes(self._instructions), self._constants)


@dataclass(init=True, frozen=True)
class Bytecode:
    instructions: bytes
    constants: List[object.Object]
