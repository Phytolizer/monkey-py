from abc import abstractmethod, ABC
from enum import Enum, auto

class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    NULL = auto()

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
