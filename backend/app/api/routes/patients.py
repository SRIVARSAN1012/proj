from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ClinicalAssessment, FollowUp, Patient
from app.schemas import AssessmentCreate, FollowUpCreate, PatientCreate, PatientUpdate
from app.services.file_service import save_xray
from app.core.config import settings

router = APIRouter(prefix="/api/patients", tags=["patients"])


def serialize_patient(patient: Patient) -> dict:
    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "age": patient.age,
        "sex": patient.sex,
        "fracture_type": patient.fracture_type,
        "side": patient.side,
        "anatomical_site": patient.anatomical_site,
        "comorbidities": patient.comorbidities,
        "smoking": patient.smoking,
        "created_at": patient.created_at.isoformat(),
        "assessments": [{
            "id": assessment.id,
            "visit_date": assessment.visit_date.isoformat(),
            "pain_score": assessment.pain_score,
            "rom_score": assessment.rom_score,
            "muscle_strength": assessment.muscle_strength,
            "gait_score": assessment.gait_score,
            "adherence_pct": assessment.adherence_pct,
            "protein_g": assessment.protein_g,
            "calories_kcal": assessment.calories_kcal,
            "weight_kg": assessment.weight_kg,
            "xray_grade": assessment.xray_grade,
            "fracture_displacement": assessment.fracture_displacement,
            "ost_open": assessment.ost_open,
            "notes": assessment.notes,
            "image_path": assessment.image_path,
        } for assessment in patient.assessments],
        "followups": [{
            "id": followup.id,
            "followup_date": followup.followup_date.isoformat(),
            "weight_kg": followup.weight_kg,
            "pain_score": followup.pain_score,
            "gait_score": followup.gait_score,
            "mobility_index": followup.mobility_index,
            "adherence_pct": followup.adherence_pct,
            "notes": followup.notes,
        } for followup in patient.followups],
    }


@router.get("")
def list_patients(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    sort_by: str = "created_at",
):
    patients = db.query(Patient)
    if search:
        like = f"%{search}%"
        patients = patients.filter(Patient.full_name.ilike(like) | Patient.fracture_type.ilike(like))
    if sort_by == "age":
        patients = patients.order_by(Patient.age.asc())
    elif sort_by == "name":
        patients = patients.order_by(Patient.full_name.asc())
    else:
        patients = patients.order_by(Patient.created_at.desc())

    total = patients.count()
    items = patients.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [serialize_patient(patient) for patient in items],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return serialize_patient(patient)


@router.patch("/{patient_id}")
def patch_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in payload.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"deleted": True, "patient_id": patient_id}


@router.post("/{patient_id}/assessments")
def create_assessment(patient_id: int, payload: AssessmentCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    assessment = ClinicalAssessment(patient_id=patient_id, **payload.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/{patient_id}/history")
def patient_history(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "patient": serialize_patient(patient),
        "predictions": [{
            "id": prediction.id,
            "created_at": prediction.created_at.isoformat(),
            "recovery_probability": prediction.recovery_probability,
            "predicted_days": prediction.predicted_days,
            "delayed_risk": prediction.delayed_risk,
            "model_label": prediction.model_label,
            "explanation": prediction.explanation,
        } for prediction in sorted(patient.predictions, key=lambda item: item.created_at, reverse=True)],
    }


@router.get("/{patient_id}/assessments")
def patient_assessments(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return [{
        "id": assessment.id,
        "patient_id": assessment.patient_id,
        "visit_date": assessment.visit_date.isoformat(),
        "pain_score": assessment.pain_score,
        "gait_score": assessment.gait_score,
        "muscle_strength": assessment.muscle_strength,
        "adherence_pct": assessment.adherence_pct,
        "image_path": assessment.image_path,
    } for assessment in patient.assessments]


@router.post("/{patient_id}/followups")
def create_followup(patient_id: int, payload: FollowUpCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    followup = FollowUp(patient_id=patient_id, **payload.model_dump())
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


@router.post("/{patient_id}/upload")
async def upload_image(patient_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    assessment = (
        db.query(ClinicalAssessment)
        .filter(ClinicalAssessment.patient_id == patient_id)
        .order_by(ClinicalAssessment.visit_date.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=409, detail="Create an assessment before attaching an X-ray")
    try:
        assessment.image_path = await save_xray(file, settings.max_upload_size_mb)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    db.commit()
    return {"status": "stored", "assessment_id": assessment.id, "image_url": f"/api/assessments/{assessment.id}/xray"}
