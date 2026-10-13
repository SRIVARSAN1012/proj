from __future__ import annotations

import json

from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score

from train_multimodal import build_synthetic_dataset, train_models


if __name__ == "__main__":
    X, labels, days = build_synthetic_dataset()
    manifest = train_models()
    print("Evaluation report")
    print(json.dumps(manifest["metrics"], indent=2))
    print("Note: evaluation is based on synthetic data only and should not be interpreted as clinical performance.")
