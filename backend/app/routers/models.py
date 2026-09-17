"""Models and metrics registry router."""

from fastapi import APIRouter
from backend.app.schemas.model import ModelRegistryResponse
from backend.app.services.model_service import get_model_registry_info

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("/registry", response_model=ModelRegistryResponse)
def get_registry():
    """Retrieves authoritative metrics and model metadata for Phase 3, Phase 7, and Phase 9."""
    return get_model_registry_info()
