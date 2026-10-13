class DenseNet121Wrapper:
    def __init__(self):
        self.kind = "densenet121"
    def status(self):
        return {"status": "not_trained", "model": self.kind, "message": "DenseNet121 checkpoint not available in demo mode"}
