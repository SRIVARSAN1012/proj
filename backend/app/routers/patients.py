from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ClinicalAssessment, FollowUp, Patient
from app.schemas import AssessmentCreate, FollowUpCreate, PatientCreate
from app.service.demo import build_demo_patients, synthetic_prediction_for_patient

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("")
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).order_by(Patient.id.asc()).all()
    if not patients:
        demo_patients = build_demo_patients()
        return demo_patients
    return [
        {
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
            "assessments": [
                {
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
                } for assessment in patient.assessments
            ],
            "followups": [
                {
                    "id": followup.id,
                    "followup_date": followup.followup_date.isoformat(),
                    "weight_kg": followup.weight_kg,
                    "pain_score": followup.pain_score,
                    "gait_score": followup.gait_score,
                    "mobility_index": followup.mobility_index,
                    "adherence_pct": followup.adherence_pct,
                    "notes": followup.notes,
                } for followup in patient.followups
            ],
        } for patient in patients
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(
        full_name=payload.full_name,
        age=payload.age,
        sex=payload.sex,
        fracture_type=payload.fracture_type,
        side=payload.side,
        anatomical_site=payload.anatomical_site,
        comorbidities=payload.comorbidities,
        smoking=payload.smoking,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

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
        "assessments": [
            {
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
            } for assessment in patient.assessments
        ],
        "followups": [
            {
                "id": followup.id,
                "followup_date": followup.followup_date.isoformat(),
                "weight_kg": followup.weight_kg,
                "pain_score": followup.pain_score,
                "gait_score": followup.gait_score,
                "mobility_index": followup.mobility_index,
                "adherence_pct": followup.adherence_pct,
                "notes": followup.notes,
            } for followup in patient.followups
        ],
    }


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
def upload_image(patient_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    upload_dir = Path(__file__).resolve().parents[2] / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{patient_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename or 'xray.png'}"
    destination = upload_dir / safe_name
    destination.write_bytes(file.file.read())

    assessment = ClinicalAssessment(
        patient_id=patient_id,
        pain_score=0.0,
        rom_score=0.0,
        muscle_strength=0.0,
        gait_score=0.0,
        adherence_pct=0.0,
        protein_g=0.0,
        calories_kcal=0.0,
        weight_kg=0.0,
        xray_grade=0.0,
        fracture_displacement=0.0,
        ost_open=False,
        image_path=str(destination),
    )
    db.add(assessment)
    db.commit()
    return {"filename": safe_name, "path": str(destination), "status": "uploaded"}

@router.get("/{patient_id}/history")
def get_history(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "patient": patient.full_name,
        "assessments": [
            {
                "id": assessment.id,
                "date": assessment.visit_date.isoformat(),
                "pain_score": assessment.pain_score,
                "gait_score": assessment.gait_score,
                "muscle_strength": assessment.muscle_strength,
                "adherence_pct": assessment.adherence_pct,
            } for assessment in patient.assessments
        ],
        "followups": [
            {
                "id": followup.id,
                "date": followup.followup_date.isoformat(),
                "mobility_index": followup.mobility_index,
                "gait_score": followup.gait_score,
                "adherence_pct": followup.adherence_pct,
            } for followup in patient.followups
        ],
    }
