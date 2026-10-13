from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import Base, get_db
from app.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def teardown_module():
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def create_patient():
    return client.post(
        "/api/patients",
        json={
            "full_name": "Jamie Smith",
            "age": 52,
            "sex": "Male",
            "fracture_type": "Tibial plateau",
            "side": "Left",
            "anatomical_site": "Tibia",
            "comorbidities": "Obesity",
            "smoking": False,
        },
    )


def make_png():
    image = Image.new("RGB", (16, 16), color="white")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_health_and_model_status_are_honest():
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    response = client.get("/api/model-status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["demo_mode"] is True
    assert payload["metrics"] is None
    assert payload["status"] == "demo_only"


def test_complete_patient_assessment_prediction_followup_xray_and_report_workflow(monkeypatch, tmp_path):
    from app.api.routes import assessments
    from app.services import file_service

    monkeypatch.setattr(file_service, "upload_directory", lambda: tmp_path)
    monkeypatch.setattr(assessments, "upload_directory", lambda: tmp_path)
    patient_response = create_patient()
    assert patient_response.status_code == 201, patient_response.text
    patient_id = patient_response.json()["id"]

    listed = client.get("/api/patients")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == patient_id
    updated = client.patch(f"/api/patients/{patient_id}", json={"age": 53})
    assert updated.status_code == 200
    assert updated.json()["age"] == 53
    rejected_update = client.patch(f"/api/patients/{patient_id}", json={"age": 200})
    assert rejected_update.status_code == 422

    assessment_data = {
        "pain_score": 6.0,
        "rom_score": 65.0,
        "muscle_strength": 3.0,
        "gait_score": 58.0,
        "adherence_pct": 78.0,
        "protein_g": 70.0,
        "calories_kcal": 2200.0,
        "weight_kg": 79.0,
        "xray_grade": 68.0,
        "fracture_displacement": 15.0,
        "ost_open": False,
        "notes": "Follow-up assessment",
    }
    assessment_response = client.post(f"/api/patients/{patient_id}/assessments", json=assessment_data)
    assert assessment_response.status_code == 200, assessment_response.text
    assessment_id = assessment_response.json()["id"]

    image_response = client.post(
        f"/api/assessments/{assessment_id}/xray",
        files={"file": ("xray.png", make_png(), "image/png")},
    )
    assert image_response.status_code == 200, image_response.text
    assert client.get(f"/api/assessments/{assessment_id}/xray").headers["content-type"] == "image/png"

    prediction_response = client.post(
        "/api/predictions",
        json={"patient_id": patient_id, "assessment": assessment_data},
    )
    assert prediction_response.status_code == 200, prediction_response.text
    prediction = prediction_response.json()
    assert prediction["recovery_probability"] > 0
    assert prediction["predicted_days"] > 0
    assert prediction["status"] == "demo_only"
    assert prediction["warnings"]

    followup_response = client.post(
        f"/api/patients/{patient_id}/followups",
        json={
            "weight_kg": 78.5,
            "pain_score": 4.5,
            "gait_score": 64,
            "mobility_index": 67,
            "adherence_pct": 86,
            "notes": "Steady improvement",
        },
    )
    assert followup_response.status_code == 200, followup_response.text

    history = client.get(f"/api/patients/{patient_id}/history")
    assert history.status_code == 200
    assert len(history.json()["patient"]["assessments"]) == 1
    assert len(history.json()["patient"]["followups"]) == 1
    assert len(history.json()["predictions"]) == 1
    assert history.json()["patient"]["assessments"][0]["image_path"]

    assert client.get("/api/dashboard/summary").json()["prediction_count"] == 1
    report = client.get(f"/api/reports/{patient_id}")
    assert report.status_code == 200
    assert report.headers["content-type"] == "application/pdf"
    assert report.content.startswith(b"%PDF")


def test_invalid_assessment_and_xray_uploads_are_rejected():
    patient_id = create_patient().json()["id"]
    invalid_assessment = client.post(
        f"/api/patients/{patient_id}/assessments",
        json={"pain_score": 20},
    )
    assert invalid_assessment.status_code == 422

    valid_assessment = client.post(f"/api/patients/{patient_id}/assessments", json={})
    assessment_id = valid_assessment.json()["id"]
    invalid_image = client.post(
        f"/api/assessments/{assessment_id}/xray",
        files={"file": ("fake.png", b"not an image", "image/png")},
    )
    assert invalid_image.status_code == 400
