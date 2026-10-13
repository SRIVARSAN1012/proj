from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
ARTIFACTS.mkdir(exist_ok=True, parents=True)


def build_synthetic_dataset(n_samples: int = 300) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    age = rng.integers(18, 86, size=n_samples)
    gait = rng.uniform(30, 90, size=n_samples)
    strength = rng.uniform(1.5, 5.5, size=n_samples)
    adherence = rng.uniform(40, 100, size=n_samples)
    xray = rng.uniform(30, 95, size=n_samples)
    protein = rng.uniform(30, 110, size=n_samples)
    pain = rng.uniform(2, 9, size=n_samples)
    features = np.column_stack([age, gait, strength, adherence, xray, protein, pain])
    delayed = ((100 - gait) / 100 + (5 - strength) / 10 + (100 - adherence) / 150 + (90 - xray) / 150 + (5 - pain) / 20 + age / 300)
    delay_labels = (delayed > 0.62).astype(int)
    recovery_days = 120 - gait * 0.7 + strength * 12 + adherence * 0.3 + xray * 0.15 - age * 0.2 + rng.normal(0, 8, size=n_samples)
    recovery_days = np.clip(recovery_days, 25, 220)
    return features, delay_labels, recovery_days


def train_models() -> dict:
    X, delayed_labels, recovery_days = build_synthetic_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, delayed_labels, test_size=0.25, random_state=42, stratify=delayed_labels)
    reg_train_X, reg_test_X, reg_train_y, reg_test_y = train_test_split(X, recovery_days, test_size=0.25, random_state=42)

    clf = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=6)
    clf.fit(X_train, y_train)
    baseline = LogisticRegression(max_iter=500)
    baseline.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    reg = RandomForestRegressor(n_estimators=250, random_state=42, max_depth=8)
    reg.fit(reg_train_X, reg_train_y)
    reg_predictions = reg.predict(reg_test_X)
    mae = mean_absolute_error(reg_test_y, reg_predictions)
    r2 = r2_score(reg_test_y, reg_predictions)

    manifest = {
        "radiology_model": "dense_net_121",
        "clinical_model": "random_forest",
        "fusion_model": "multimodal_fusion",
        "baseline_model": "logistic_regression",
        "last_training": "synthetic_demo_dataset",
        "notes": "This script is intentionally built on synthetic data to allow the prototype to run without external datasets.",
        "metrics": {
            "classification_accuracy": round(float(accuracy), 4),
            "regression_mae_days": round(float(mae), 3),
            "regression_r2": round(float(r2), 4),
            "baseline_accuracy": round(float(accuracy_score(y_test, baseline.predict(X_test))), 4),
        },
    }
    (ARTIFACTS / "model_manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    print(json.dumps(train_models(), indent=2))
