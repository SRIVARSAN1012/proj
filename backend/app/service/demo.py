from __future__ import annotations

from datetime import datetime
from typing import Any


def build_demo_patients() -> list[dict[str, Any]]:
    return [
        {
            "id": 1,
            "full_name": "Alicia Moreno",
            "age": 43,
            "sex": "Female",
            "fracture_type": "Transverse femoral shaft",
            "side": "Left",
            "anatomical_site": "Femur",
            "comorbidities": "Osteopenia",
            "smoking": False,
            "created_at": datetime.utcnow().isoformat(),
            "assessments": [{
                "id": 1,
                "visit_date": datetime.utcnow().isoformat(),
                "pain_score": 6.5,
                "rom_score": 68.0,
                "muscle_strength": 3.6,
                "gait_score": 57.0,
                "adherence_pct": 82.0,
                "protein_g": 72.0,
                "calories_kcal": 2100.0,
                "weight_kg": 68.0,
                "xray_grade": 72.0,
                "fracture_displacement": 12.0,
                "ost_open": False,
                "notes": "Ambulation is improving; no early complications.",
                "image_path": None,
            }],
            "followups": [{
                "id": 1,
                "followup_date": datetime.utcnow().isoformat(),
                "weight_kg": 67.8,
                "pain_score": 4.8,
                "gait_score": 63.0,
                "mobility_index": 68.0,
                "adherence_pct": 88.0,
                "notes": "Consistent physiotherapy adherence.",
            }],
        },
        {
            "id": 2,
            "full_name": "Daniel Brooks",
            "age": 61,
            "sex": "Male",
            "fracture_type": "Intertrochanteric",
            "side": "Right",
            "anatomical_site": "Hip",
            "comorbidities": "Diabetes, hypertension",
            "smoking": True,
            "created_at": datetime.utcnow().isoformat(),
            "assessments": [{
                "id": 2,
                "visit_date": datetime.utcnow().isoformat(),
                "pain_score": 7.8,
                "rom_score": 55.0,
                "muscle_strength": 2.9,
                "gait_score": 46.0,
                "adherence_pct": 70.0,
                "protein_g": 64.0,
                "calories_kcal": 1980.0,
                "weight_kg": 75.0,
                "xray_grade": 63.0,
                "fracture_displacement": 22.0,
                "ost_open": False,
                "notes": "Recovery risk elevated due to diabetes and poor adherence.",
                "image_path": None,
            }],
            "followups": [{
                "id": 2,
                "followup_date": datetime.utcnow().isoformat(),
                "weight_kg": 74.2,
                "pain_score": 6.4,
                "gait_score": 49.0,
                "mobility_index": 54.0,
                "adherence_pct": 72.0,
                "notes": "Foot drop and reduced endurance remain concerns.",
            }],
        },
    ]


def synthetic_explanation() -> list[dict[str, float | str]]:
    return [
        {"feature": "gait_score", "importance": 0.28},
        {"feature": "muscle_strength", "importance": 0.22},
        {"feature": "adherence_pct", "importance": 0.17},
        {"feature": "xray_grade", "importance": 0.15},
        {"feature": "protein_g", "importance": 0.09},
        {"feature": "pain_score", "importance": 0.06},
        {"feature": "age", "importance": 0.03},
    ]


def synthetic_prediction_for_patient(patient: dict[str, Any], assessment: dict[str, Any] | None = None) -> dict[str, Any]:
    age = patient.get("age", 50)
    gait = (assessment or {}).get("gait_score", 60)
    strength = (assessment or {}).get("muscle_strength", 3.5)
    adherence = (assessment or {}).get("adherence_pct", 80)
    fracture = 1 if patient.get("fracture_type", "").lower().find("intertrochanteric") >= 0 else 0
    risk_signal = (100 - gait) / 100 + max(0, 0.5 - strength / 10) + max(0, 0.5 - adherence / 100) + fracture * 0.18 + age / 200
    recovery_probability = max(0.15, min(0.92, 0.88 - risk_signal * 0.8))
    predicted_days = round(128 - recovery_probability * 72 + fracture * 22, 1)
    delayed_risk = round(max(0.08, min(0.9, 1.0 - recovery_probability + fracture * 0.15 + (100 - adherence) / 250)), 3)
    return {
        "recovery_probability": round(float(recovery_probability), 3),
        "predicted_days": predicted_days,
        "delayed_risk": delayed_risk,
        "model_label": "rehab_twin_multimodal",
        "explanation": synthetic_explanation(),
        "notes": "Local recovery estimate only. Not a validated clinical prediction or diagnosis.",
    }
