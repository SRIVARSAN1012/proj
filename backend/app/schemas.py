from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
    full_name: str
    age: int
    sex: str
    fracture_type: str
    side: str
    anatomical_site: str
    comorbidities: str = ""
    smoking: bool = False


class AssessmentCreate(BaseModel):
    pain_score: float = 0.0
    rom_score: float = 0.0
    muscle_strength: float = 0.0
    gait_score: float = 0.0
    adherence_pct: float = 0.0
    protein_g: float = 0.0
    calories_kcal: float = 0.0
    weight_kg: float = 0.0
    xray_grade: float = 0.0
    fracture_displacement: float = 0.0
    ost_open: bool = False
    notes: Optional[str] = None


class FollowUpCreate(BaseModel):
    weight_kg: float = 0.0
    pain_score: float = 0.0
    gait_score: float = 0.0
    mobility_index: float = 0.0
    adherence_pct: float = 0.0
    notes: Optional[str] = None


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
