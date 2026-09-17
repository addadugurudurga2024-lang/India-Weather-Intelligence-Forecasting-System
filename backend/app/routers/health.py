"""Health and status endpoint."""

from fastapi import APIRouter
from backend.app.services.data_service import load_stations
from backend.app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Returns application health, version, and component status."""
    stns = load_stations()
    return {
        "status": "HEALTHY",
        "system": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "canonical_stations_count": len(stns),
        "phase7_models_verified": 84,
        "phase9_models_verified": 7,
    }
