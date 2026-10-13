from __future__ import annotations

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    from app.models import ClinicalAssessment, FollowUp, Patient

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        demo_patient = db.query(Patient).filter(Patient.full_name.like("Demo patient - %")).first()
        if demo_patient:
            return

        demo_patients = [
            Patient(
                full_name="Demo patient - Alicia Moreno",
                age=43,
                sex="Female",
                fracture_type="Transverse femoral shaft",
                side="Left",
                anatomical_site="Femur",
                comorbidities="Osteopenia",
                smoking=False,
            ),
            Patient(
                full_name="Demo patient - Daniel Brooks",
                age=61,
                sex="Male",
                fracture_type="Intertrochanteric",
                side="Right",
                anatomical_site="Hip",
                comorbidities="Diabetes, hypertension",
                smoking=True,
            ),
        ]
        db.add_all(demo_patients)
        db.flush()
        db.add_all([
            ClinicalAssessment(
                patient_id=demo_patients[0].id,
                pain_score=6.5,
                rom_score=68,
                muscle_strength=3.6,
                gait_score=57,
                adherence_pct=82,
                protein_g=72,
                calories_kcal=2100,
                weight_kg=68,
                xray_grade=72,
                fracture_displacement=12,
                notes="Synthetic demo record. Ambulation is improving.",
            ),
            ClinicalAssessment(
                patient_id=demo_patients[1].id,
                pain_score=7.8,
                rom_score=55,
                muscle_strength=2.9,
                gait_score=46,
                adherence_pct=70,
                protein_g=64,
                calories_kcal=1980,
                weight_kg=75,
                xray_grade=63,
                fracture_displacement=22,
                notes="Synthetic demo record. Used only to demonstrate risk factors.",
            ),
            FollowUp(
                patient_id=demo_patients[0].id,
                weight_kg=67.8,
                pain_score=4.8,
                gait_score=63,
                mobility_index=68,
                adherence_pct=88,
                notes="Synthetic demo follow-up.",
            ),
            FollowUp(
                patient_id=demo_patients[1].id,
                weight_kg=74.2,
                pain_score=6.4,
                gait_score=49,
                mobility_index=54,
                adherence_pct=72,
                notes="Synthetic demo follow-up.",
            ),
        ])
        db.commit()
