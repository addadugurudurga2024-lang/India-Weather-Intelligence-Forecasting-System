"""AI Weather Intelligence router."""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.intelligence import (
    QuestionRequest,
    QuestionResponse,
    IntelligenceSummaryResponse,
    RiskAssessmentResponse,
)
from backend.app.services.data_service import get_station_by_id
from backend.app.services.intelligence_service import (
    answer_weather_query,
    get_intelligence_summary,
    get_risk_assessment,
)

router = APIRouter(prefix="/intelligence", tags=["AI Intelligence"])


@router.post("/query", response_model=QuestionResponse)
def post_query(request: QuestionRequest):
    """Answers a meteorological query using Phase 8 zero-hallucination routing."""
    stn = get_station_by_id(request.station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{request.station_id}' not found in the 413 canonical station registry.",
        )
    return answer_weather_query(request.station_id, request.question)


@router.get("/summary/{station_id}", response_model=IntelligenceSummaryResponse)
def get_summary(station_id: str):
    """Retrieves structured AI weather intelligence summary for a station."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    return get_intelligence_summary(station_id)


@router.get("/risk/{station_id}", response_model=RiskAssessmentResponse)
def get_risk(station_id: str):
    """Retrieves precipitation and severe weather risk assessment."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    return get_risk_assessment(station_id)
