from abc import abstractmethod, ABC
from enum import Enum, auto


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    NULL = auto()
    RETURN_VALUE = auto()
    ERROR = auto()

    def __str__(self):
        if self == ObjectType.INTEGER:
            return "INTEGER"
        elif self == ObjectType.BOOLEAN:
            return "BOOLEAN"
        elif self == ObjectType.NULL:
            return "NULL"
        else:
            raise Exception("unexpected type for __str__")


class Object(ABC):
    @abstractmethod
    def type(self):
        pass

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
