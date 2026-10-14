from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Prediction, Patient
from app.schemas import PredictionRequest
from app.service.model_service import predict_patient

router = APIRouter(prefix="/api", tags=["predictions"])

@router.post("/predictions")
def create_prediction(payload: PredictionRequest, db: Session = Depends(get_db)):
    patient_id = payload.patient_id
    if patient_id is None:
        raise HTTPException(status_code=400, detail="patient_id is required")
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    assessment = payload.assessment.model_dump() if payload.assessment else {
        "muscle_strength": 3.5,
        "gait_score": 60,
        "adherence_pct": 80,
        "pain_score": 5,
    }
    result = predict_patient({"id": patient.id, "full_name": patient.full_name, "age": patient.age, "sex": patient.sex, "fracture_type": patient.fracture_type}, assessment)
    record = Prediction(patient_id=patient.id, recovery_probability=result["recovery_probability"], predicted_days=result["predicted_days"], delayed_risk=result["delayed_risk"], model_label=result["model_label"], explanation=result.get("explanation", []))
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "patient_id": patient.id,
        "created_at": record.created_at.isoformat(),
        "recovery_probability": record.recovery_probability,
        "predicted_days": record.predicted_days,
        "delayed_risk": record.delayed_risk,
        "model_label": record.model_label,
        "explanation": record.explanation,
        "status": "local_research_only",
        "warnings": ["Local recovery estimate only. Not a validated clinical prediction."],
    }

@router.get("/predictions/{prediction_id}")
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {
        "id": record.id,
        "patient_id": record.patient_id,
        "created_at": record.created_at.isoformat(),
        "recovery_probability": record.recovery_probability,
        "predicted_days": record.predicted_days,
        "delayed_risk": record.delayed_risk,
        "model_label": record.model_label,
        "explanation": record.explanation,
    }

@router.get("/patients/{patient_id}/predictions")
def patient_predictions(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    records = db.query(Prediction).filter(Prediction.patient_id == patient_id).order_by(Prediction.created_at.desc()).all()
    return [{
        "id": record.id,
        "patient_id": record.patient_id,
        "created_at": record.created_at.isoformat(),
        "recovery_probability": record.recovery_probability,
        "predicted_days": record.predicted_days,
        "delayed_risk": record.delayed_risk,
        "model_label": record.model_label,
    } for record in records]

@router.get("/predictions/{prediction_id}/explanations")
def get_explanations(prediction_id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {"prediction_id": prediction_id, "explanation": record.explanation or []}

@router.get("/predictions/{prediction_id}/gradcam")
def get_gradcam(prediction_id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {"prediction_id": prediction_id, "status": "not_available", "explanation": "Grad-CAM is only generated when a compatible trained radiology model and checkpoint are available."}
