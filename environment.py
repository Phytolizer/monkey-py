class Environment:
    def __init__(self, outer=None):
        self.store = dict()
        self.outer = outer

    def get(self, name):
        try:
            return self.store[name]
        except KeyError:
            if self.outer is not None:
                return self.outer.get(name)
            raise

    def set(self, name, value):
        self.store[name] = value
