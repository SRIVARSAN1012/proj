from fastapi import APIRouter

from app.api.routes.assessments import router as assessments_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.patients import router as patients_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.reports import router as reports_router

router = APIRouter()
router.include_router(health_router)
router.include_router(patients_router)
router.include_router(assessments_router)
router.include_router(predictions_router)
router.include_router(dashboard_router)
router.include_router(reports_router)
