from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Patient

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{patient_id}")
def generate_report(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("REHAB-TWIN Clinical Recovery Summary", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Patient: {patient.full_name}", styles["Heading2"]),
        Paragraph(f"Age: {patient.age} | Sex: {patient.sex} | Fracture: {patient.fracture_type}", styles["BodyText"]),
        Paragraph(f"Anatomic site: {patient.anatomical_site} | Side: {patient.side}", styles["BodyText"]),
        Paragraph("Clinical safety notice: This is a research prototype and not a certified medical device. It should not replace clinician judgment.", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("This report is generated for demonstration purposes only. It must be reviewed by a licensed clinician before any clinical action.", styles["BodyText"]),
    ]
    doc.build(story)
    pdf_data = buffer.getvalue()
    return StreamingResponse(
        BytesIO(pdf_data),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rehab_twin_report_patient_{patient_id}.pdf"},
    )
