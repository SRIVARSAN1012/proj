from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[str] = mapped_column(String(20), nullable=False)
    fracture_type: Mapped[str] = mapped_column(String(100), nullable=False)
    side: Mapped[str] = mapped_column(String(20), nullable=False)
    anatomical_site: Mapped[str] = mapped_column(String(100), nullable=False)
    comorbidities: Mapped[str] = mapped_column(String(255), default="")
    smoking: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assessments: Mapped[list["ClinicalAssessment"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    followups: Mapped[list["FollowUp"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class ClinicalAssessment(Base):
    __tablename__ = "clinical_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    visit_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    pain_score: Mapped[float] = mapped_column(Float, default=0.0)
    rom_score: Mapped[float] = mapped_column(Float, default=0.0)
    muscle_strength: Mapped[float] = mapped_column(Float, default=0.0)
    gait_score: Mapped[float] = mapped_column(Float, default=0.0)
    adherence_pct: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    calories_kcal: Mapped[float] = mapped_column(Float, default=0.0)
    weight_kg: Mapped[float] = mapped_column(Float, default=0.0)
    xray_grade: Mapped[float] = mapped_column(Float, default=0.0)
    fracture_displacement: Mapped[float] = mapped_column(Float, default=0.0)
    ost_open: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, default=None)
    image_path: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    patient: Mapped[Patient] = relationship(back_populates="assessments")


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    followup_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    weight_kg: Mapped[float] = mapped_column(Float, default=0.0)
    pain_score: Mapped[float] = mapped_column(Float, default=0.0)
    gait_score: Mapped[float] = mapped_column(Float, default=0.0)
    mobility_index: Mapped[float] = mapped_column(Float, default=0.0)
    adherence_pct: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, default=None)
    patient: Mapped[Patient] = relationship(back_populates="followups")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    recovery_probability: Mapped[float] = mapped_column(Float, default=0.0)
    predicted_days: Mapped[float] = mapped_column(Float, default=0.0)
    delayed_risk: Mapped[float] = mapped_column(Float, default=0.0)
    model_label: Mapped[str] = mapped_column(String(100), default="synthetic")
    explanation: Mapped[dict] = mapped_column(JSON, default=dict)
    patient: Mapped[Patient] = relationship(back_populates="predictions")
