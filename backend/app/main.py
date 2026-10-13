from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.core.config import settings
from app.db import init_db

init_db()

app = FastAPI(
    title="REHAB-TWIN",
    description="Explainable multimodal AI for predicting functional recovery after lower-limb fractures.",
    version="0.1.0",
)

origins = [origin.strip() for origin in settings.frontend_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict:
    return {"message": "REHAB-TWIN API is running", "status": "demo_mode"}
