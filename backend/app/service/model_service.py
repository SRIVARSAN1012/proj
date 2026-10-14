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
                "status": "local_research_only",
                "prototype_mode": True,
                "radiology_model": "unavailable",
                "clinical_model": "local research configuration",
                "fusion_model": "unavailable",
                "last_training": payload.get("last_training"),
                "metrics": None,
                "notes": "The available manifest describes a local research configuration. No clinically trained model artifacts are available.",
            }
        return {
            "status": "artifacts_present_unvalidated",
            "prototype_mode": True,
            "radiology_model": payload.get("radiology_model", "unavailable"),
            "clinical_model": payload.get("clinical_model", "unavailable"),
            "fusion_model": payload.get("fusion_model", "unavailable"),
            "last_training": payload.get("last_training"),
            "metrics": None,
            "notes": "Artifacts are present but have not been verified as clinically validated. Local research mode remains enabled.",
        }

    return {
        "status": "local_research_only",
        "prototype_mode": True,
        "radiology_model": "unavailable",
        "clinical_model": "unavailable",
        "fusion_model": "unavailable",
        "last_training": None,
        "metrics": None,
        "notes": "No trained weights found. The app is running in local research mode and should not be used as a clinical decision tool.",
    }


def predict_patient(patient: dict[str, Any], assessment: dict[str, Any] | None = None) -> dict[str, Any]:
    return synthetic_prediction_for_patient(patient, assessment)


def save_manifest(payload: dict[str, Any]) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    (MODEL_DIR / "model_manifest.json").write_text(json.dumps(payload, indent=2))
