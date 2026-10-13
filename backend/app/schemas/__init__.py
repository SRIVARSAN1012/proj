from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    age: int = Field(ge=0, le=120)
    sex: str = Field(min_length=1, max_length=20)
    fracture_type: str = Field(min_length=1, max_length=100)
    side: str = Field(min_length=1, max_length=20)
    anatomical_site: str = Field(min_length=1, max_length=100)
    comorbidities: str = Field(default="", max_length=255)
    smoking: bool = False


class PatientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    age: int | None = Field(default=None, ge=0, le=120)
    sex: str | None = Field(default=None, min_length=1, max_length=20)
    fracture_type: str | None = Field(default=None, min_length=1, max_length=100)
    side: str | None = Field(default=None, min_length=1, max_length=20)
    anatomical_site: str | None = Field(default=None, min_length=1, max_length=100)
    comorbidities: str | None = Field(default=None, max_length=255)
    smoking: bool | None = None


class AssessmentCreate(BaseModel):
    pain_score: float = Field(default=0.0, ge=0, le=10)
    rom_score: float = Field(default=0.0, ge=0, le=100)
    muscle_strength: float = Field(default=0.0, ge=0, le=5)
    gait_score: float = Field(default=0.0, ge=0, le=100)
    adherence_pct: float = Field(default=0.0, ge=0, le=100)
    protein_g: float = Field(default=0.0, ge=0, le=500)
    calories_kcal: float = Field(default=0.0, ge=0, le=10000)
    weight_kg: float = Field(default=0.0, ge=0, le=500)
    xray_grade: float = Field(default=0.0, ge=0, le=100)
    fracture_displacement: float = Field(default=0.0, ge=0, le=100)
    ost_open: bool = False
    notes: Optional[str] = Field(default=None, max_length=4000)


class FollowUpCreate(BaseModel):
    weight_kg: float = Field(default=0.0, ge=0, le=500)
    pain_score: float = Field(default=0.0, ge=0, le=10)
    gait_score: float = Field(default=0.0, ge=0, le=100)
    mobility_index: float = Field(default=0.0, ge=0, le=100)
    adherence_pct: float = Field(default=0.0, ge=0, le=100)
    notes: Optional[str] = Field(default=None, max_length=4000)


class PredictionRequest(BaseModel):
    patient_id: Optional[int] = None
    symptoms: dict[str, Any] = Field(default_factory=dict)
    assessment: Optional[AssessmentCreate] = None


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    age: int
    sex: str
    fracture_type: str
    side: str
    anatomical_site: str
    comorbidities: str
    smoking: bool
    created_at: datetime


class AssessmentOut(PatientOut):
    pass


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    patient_id: int
    recovery_probability: float
    predicted_days: float
    delayed_risk: float
    model_label: str
    explanation: dict
    created_at: datetime


__all__ = [
    "PatientCreate",
    "PatientUpdate",
    "AssessmentCreate",
    "FollowUpCreate",
    "PredictionRequest",
    "PatientOut",
    "AssessmentOut",
    "PredictionOut",
]
