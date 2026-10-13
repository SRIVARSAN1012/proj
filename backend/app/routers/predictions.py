from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Patient, Prediction
from app.schemas import PredictionRequest
from app.service.model_service import predict_patient

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("")
def create_prediction(payload: PredictionRequest, db: Session = Depends(get_db)):
    patient_id = payload.patient_id
    if patient_id is None:
        patient_id = 1
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    assessment = payload.assessment.model_dump() if payload.assessment else {
        "muscle_strength": 3.5,
        "gait_score": 60,
        "adherence_pct": 80,
        "pain_score": 5,
    }
    result = predict_patient({
        "id": patient.id,
        "full_name": patient.full_name,
        "age": patient.age,
        "sex": patient.sex,
        "fracture_type": patient.fracture_type,
    }, assessment)

    prediction = Prediction(
        patient_id=patient.id,
        recovery_probability=result["recovery_probability"],
        predicted_days=result["predicted_days"],
        delayed_risk=result["delayed_risk"],
        model_label=result["model_label"],
        explanation=result["explanation"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        "id": prediction.id,
        "patient_id": prediction.patient_id,
        "recovery_probability": prediction.recovery_probability,
        "predicted_days": prediction.predicted_days,
        "delayed_risk": prediction.delayed_risk,
        "model_label": prediction.model_label,
        "explanation": prediction.explanation,
        "notes": result.get("notes"),
    }


@router.get("/{patient_id}")
def get_patient_predictions(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    records = db.query(Prediction).filter(Prediction.patient_id == patient_id).order_by(Prediction.created_at.desc()).all()
    return [{
        "id": record.id,
        "patient_id": record.patient_id,
        "recovery_probability": record.recovery_probability,
        "predicted_days": record.predicted_days,
        "delayed_risk": record.delayed_risk,
        "model_label": record.model_label,
        "explanation": record.explanation,
        "created_at": record.created_at.isoformat(),
    } for record in records]
