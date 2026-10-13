from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.service.demo import synthetic_prediction_for_patient

MODEL_DIR = Path(__file__).resolve().parents[2] / "artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def model_status() -> dict[str, Any]:
    manifest = MODEL_DIR / "model_manifest.json"
    if manifest.exists():
        payload = json.loads(manifest.read_text())
        synthetic_training = payload.get("last_training") == "synthetic_demo_dataset"
        if synthetic_training:
            return {
                "status": "demo_only",
                "demo_mode": True,
                "radiology_model": "unavailable",
                "clinical_model": "synthetic demonstration only",
                "fusion_model": "unavailable",
                "last_training": payload.get("last_training"),
                "metrics": None,
                "notes": "The available manifest describes synthetic demonstration data only. No clinically trained model artifacts are available.",
            }
        return {
            "status": "artifacts_present_unvalidated",
            "demo_mode": True,
            "radiology_model": payload.get("radiology_model", "unavailable"),
            "clinical_model": payload.get("clinical_model", "unavailable"),
            "fusion_model": payload.get("fusion_model", "unavailable"),
            "last_training": payload.get("last_training"),
            "metrics": None,
            "notes": "Artifacts are present but have not been verified as clinically validated. Demo mode remains enabled.",
        }

    return {
        "status": "demo_only",
        "demo_mode": True,
        "radiology_model": "unavailable",
        "clinical_model": "unavailable",
        "fusion_model": "unavailable",
        "last_training": None,
        "metrics": None,
        "notes": "No trained weights found. The app is running in synthetic demo mode and should not be used as a clinical decision tool.",
    }


def predict_patient(patient: dict[str, Any], assessment: dict[str, Any] | None = None) -> dict[str, Any]:
    return synthetic_prediction_for_patient(patient, assessment)


def save_manifest(payload: dict[str, Any]) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    (MODEL_DIR / "model_manifest.json").write_text(json.dumps(payload, indent=2))
