from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Patient

router = APIRouter(prefix="/api", tags=["reports"])

@router.get("/reports/{patient_id}")
def generate_report(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    latest_assessment = max(patient.assessments, key=lambda item: item.visit_date, default=None)
    latest_prediction = max(patient.predictions, key=lambda item: item.created_at, default=None)
    story = [
        Paragraph("REHAB-TWIN Clinical Recovery Summary", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Patient: {escape(patient.full_name)}", styles["Heading2"]),
        Paragraph(f"Age: {patient.age} | Sex: {escape(patient.sex)} | Fracture: {escape(patient.fracture_type)}", styles["BodyText"]),
        Paragraph(f"Anatomic site: {escape(patient.anatomical_site)} | Side: {escape(patient.side)}", styles["BodyText"]),
        Spacer(1, 10),
        Paragraph("Latest clinical assessment", styles["Heading2"]),
        Paragraph(
            (
                f"Visit: {latest_assessment.visit_date:%Y-%m-%d} | Pain: {latest_assessment.pain_score:g}/10 | "
                f"Strength: {latest_assessment.muscle_strength:g}/5 | Gait: {latest_assessment.gait_score:g}/100 | "
                f"Physiotherapy adherence: {latest_assessment.adherence_pct:g}%"
            ) if latest_assessment else "No clinical assessments have been recorded.",
            styles["BodyText"],
        ),
        Spacer(1, 10),
        Paragraph("Latest prediction record", styles["Heading2"]),
        Paragraph(
            (
                f"Local recovery estimate — recovery: {latest_prediction.recovery_probability:.1%}; "
                f"duration: {latest_prediction.predicted_days:.0f} days; delayed-risk estimate: {latest_prediction.delayed_risk:.1%}."
            ) if latest_prediction else "No prediction record has been generated.",
            styles["BodyText"],
        ),
        
    ]
    doc.build(story)
    pdf_data = buffer.getvalue()
    return StreamingResponse(BytesIO(pdf_data), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=rehab_twin_report_patient_{patient_id}.pdf"})
