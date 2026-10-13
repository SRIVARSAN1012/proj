class ClinicalModel:
    def __init__(self):
        self.kind = "random_forest"
    def status(self):
        return {"status": "demo_only", "model": self.kind, "message": "Synthetic demo clinical model active"}
