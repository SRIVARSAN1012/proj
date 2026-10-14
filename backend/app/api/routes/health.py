from fastapi import APIRouter

from app.service.model_service import model_status

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "REHAB-TWIN", "prototype_mode": True}

@router.get("/model-status")
def model_status_route() -> dict:
    return model_status()
