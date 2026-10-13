from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ClinicalAssessment, Patient, Prediction

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    patient_count = db.query(Patient).count()
    assessment_count = db.query(ClinicalAssessment).count()
    active_predictions = db.query(Prediction).count()
    return {
        "patient_count": patient_count,
        "assessment_count": assessment_count,
        "prediction_count": active_predictions,
        "demo_mode": True,
        "status": "research_prototype",
        "clinic_notice": "This dashboard is for research demonstration only and is not a medical device.",
    }
