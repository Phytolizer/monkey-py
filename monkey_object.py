from abc import abstractmethod, ABC
from enum import Enum, auto


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    NULL = auto()
    RETURN_VALUE = auto()
    ERROR = auto()
    FUNCTION = auto()
    STRING = auto()
    BUILTIN = auto()

    def __str__(self):
        if self == ObjectType.INTEGER:
            return "INTEGER"
        elif self == ObjectType.BOOLEAN:
            return "BOOLEAN"
        elif self == ObjectType.NULL:
            return "NULL"
        elif self == ObjectType.STRING:
            return "STRING"
        else:
            raise Exception("unexpected type for __str__")


class Object(ABC):
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def inspect(self):
        pass


class Integer(Object):
    def __init__(self, value):
        self.value = value

    def type(self):
        return ObjectType.INTEGER

    def inspect(self):
        return str(self.value)


class Boolean(Object):
    def __init__(self, value):
        self.value = value

    def type(self):
        return ObjectType.BOOLEAN

    def inspect(self):
        if self.value:
            return "true"
        else:
            return "false"


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


class String(Object):
    def __init__(self, value):
        self.value = value

    def type(self):
        return ObjectType.STRING

    def inspect(self):
        return self.value


class Builtin(Object):
    def __init__(self, fn):
        self.fn = fn

    def type(self):
        return ObjectType.BUILTIN

    def inspect(self):
        return "built-in function"
