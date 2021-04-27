from abc import abstractmethod, ABC
from enum import Enum, auto
from dataclasses import dataclass
import hashlib
import struct


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    NULL = auto()
    RETURN_VALUE = auto()
    ERROR = auto()
    FUNCTION = auto()
    STRING = auto()
    BUILTIN = auto()
    ARRAY = auto()
    HASH = auto()

    def __str__(self):
        if self == ObjectType.INTEGER:
            return "INTEGER"
        elif self == ObjectType.BOOLEAN:
            return "BOOLEAN"
        elif self == ObjectType.NULL:
            return "NULL"
        elif self == ObjectType.STRING:
            return "STRING"
        elif self == ObjectType.FUNCTION:
            return "FUNCTION"
        else:
            raise Exception("unexpected type for __str__")


class Object(ABC):
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def inspect(self):
        pass


class Hashable(ABC):
    @abstractmethod
    def hash_key(self):
        pass


@dataclass(init=True, frozen=True)
class HashKey:
    type: ObjectType
    value: int


class Integer(Object, Hashable):
    def __init__(self, value):
        self.value = value

    def type(self):
        return ObjectType.INTEGER

    def inspect(self):
        return str(self.value)

    def hash_key(self):
        return HashKey(self.type(), self.value)


class Boolean(Object, Hashable):
    def __init__(self, value):
        self.value = value

    def type(self):
        return ObjectType.BOOLEAN

    def inspect(self):
        if self.value:
            return "true"
        else:
            return "false"

    def hash_key(self):
        return HashKey(self.type(), int(self.value))


class Null(Object):
    def type(self):
        return ObjectType.NULL

    def inspect(self):
        return "null"


class ReturnValue(Object):
    def __init__(self, value):
        self.value = value

    def type(self):
        return ObjectType.RETURN_VALUE

    def inspect(self):
        return self.value.inspect()


class Error(Object):
    def __init__(self, message):
        self.message = message

    def type(self):
        return ObjectType.ERROR

    def inspect(self):
        return f"ERROR: {self.message}"


class Function(Object):
    def __init__(self, parameters, body, env):
        self.parameters = parameters
        self.body = body
        self.env = env

    def type(self):
        return ObjectType.FUNCTION

    def inspect(self):
        return f"fn({self.parameters.join(', ')}) {{\n{self.body.string()}\n}}"


class String(Object, Hashable):
    def __init__(self, value):
        self.value = value

    def type(self):
        return ObjectType.STRING

    def inspect(self):
        return self.value

    def hash_key(self):
        hasher = hashlib.shake_128()
        hasher.update(self.value.encode("utf-8"))
        bin = hasher.digest(4)
        return HashKey(self.type(), struct.unpack("<L", bin)[0])


class Builtin(Object):
    def __init__(self, fn):
        self.fn = fn

    def type(self):
        return ObjectType.BUILTIN

    def inspect(self):
        return "built-in function"


class Array(Object):
    def __init__(self, elements):
        self.elements = elements

    def type(self):
        return ObjectType.ARRAY

    def inspect(self):
        return f"[{', '.join(map(lambda e: e.inspect(), self.elements))}]"


@dataclass(init=True, frozen=True)
class HashPair:
    key: Object
    value: Object


class Hash(Object):
    def __init__(self, pairs):
        self.pairs = pairs

    def type(self):
        return ObjectType.HASH

    def inspect(self):
        pairs = []
        for pair in self.pairs.values():
            pairs.append(f"{pair.key.inspect()}: {pair.value.inspect()}")
        return f"{{{', '.join(pairs)}}}"
