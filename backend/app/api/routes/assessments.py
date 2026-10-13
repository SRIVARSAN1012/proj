from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models import ClinicalAssessment, Patient
from app.services.file_service import save_xray, upload_directory

router = APIRouter(prefix="/api", tags=["assessments"])

@router.get("/assessments")
def list_assessments(db: Session = Depends(get_db), patient_id: int | None = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    query = db.query(ClinicalAssessment)
    if patient_id is not None:
        query = query.filter(ClinicalAssessment.patient_id == patient_id)
    total = query.count()
    items = query.order_by(ClinicalAssessment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [{
        "id": assessment.id,
        "patient_id": assessment.patient_id,
        "visit_date": assessment.visit_date.isoformat(),
        "pain_score": assessment.pain_score,
        "muscle_strength": assessment.muscle_strength,
        "gait_score": assessment.gait_score,
        "adherence_pct": assessment.adherence_pct,
        "image_path": assessment.image_path,
    } for assessment in items], "page": page, "page_size": page_size, "total": total}

@router.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(ClinicalAssessment).filter(ClinicalAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {
        "id": assessment.id,
        "patient_id": assessment.patient_id,
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
    }

@router.post("/assessments/{assessment_id}/xray")
async def upload_assessment_xray(
    assessment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    assessment = db.query(ClinicalAssessment).filter(ClinicalAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    try:
        image_name = await save_xray(file, settings.max_upload_size_mb)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    assessment.image_path = image_name
    db.commit()
    return {"status": "stored", "assessment_id": assessment_id, "image_url": f"/api/assessments/{assessment_id}/xray"}

@router.get("/assessments/{assessment_id}/xray")
def get_assessment_xray(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(ClinicalAssessment).filter(ClinicalAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if not assessment.image_path:
        raise HTTPException(status_code=404, detail="No X-ray is attached to this assessment")
    image_path = upload_directory() / Path(assessment.image_path).name
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Stored X-ray file is missing")
    return FileResponse(image_path)
