class ModelRegistry:
    def __init__(self):
        self.models = {}
    def register(self, name, model):
        self.models[name] = model
    def available(self):
        return sorted(self.models.keys())
