class MultimodalFusionModel:
    def __init__(self):
        self.kind = "fusion"
    def status(self):
        return {"status": "demo_only", "model": self.kind, "message": "Fusion model is unavailable until trained checkpoints are present"}
