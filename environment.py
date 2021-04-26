class Environment:
    def __init__(self):
        self.store = dict()

    def get(self, name):
        return self.store[name]

    def set(self, name, value):
        self.store[name] = value
