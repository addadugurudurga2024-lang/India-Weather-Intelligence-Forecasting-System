"""Operational Forecast Center router."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.forecast import (
    OperationalTimelineResponse,
    MultiHorizonForecastResponse,
    CurrentTelemetryResponse,
    HorizonDiagnosticsResponse,
)
from backend.app.services.data_service import get_station_by_id
from backend.app.services.forecast_service import (
    get_operational_timeline,
    get_multi_horizon_forecast,
    get_current_telemetry,
    get_horizon_diagnostics,
)

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.get("/25day-timeline/{station_id}", response_model=OperationalTimelineResponse)
def get_timeline(
    station_id: str,
    mode: str = Query(default="historical_holdout_replay", description="'historical_holdout_replay' or 'operational_current'"),
    origin_date: Optional[str] = Query(default=None, description="Optional explicit origin date (YYYY-MM-DD)"),
):
    """Retrieves authoritative 25-day operational timeline (D-12..D-1, D0, D+1..D+12)."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    data = get_operational_timeline(station_id, mode=mode, origin_date=origin_date)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to build operational timeline.")
    return data


@router.get("/multi-horizon/{station_id}", response_model=MultiHorizonForecastResponse)
def get_forecast(
    station_id: str,
    mode: str = Query(default="historical_holdout_replay", description="'historical_holdout_replay' or 'operational_current'"),
    origin_date: Optional[str] = Query(default=None, description="Optional explicit origin date (YYYY-MM-DD)"),
):
    """Retrieves direct multi-horizon forecasts T+1 through T+12 using frozen Phase 7 models."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    data = get_multi_horizon_forecast(station_id, mode=mode, origin_date=origin_date)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to generate multi-horizon forecast.")
    return data


@router.get("/current-telemetry/{station_id}", response_model=CurrentTelemetryResponse)
def get_telemetry(
    station_id: str,
    mode: str = Query(default="historical_holdout_replay", description="'historical_holdout_replay' or 'operational_current'"),
    origin_date: Optional[str] = Query(default=None, description="Optional explicit origin date (YYYY-MM-DD)"),
):
    """Retrieves physical D0 observation telemetry. Zero ML fallback allowed."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    data = get_current_telemetry(station_id, mode=mode, origin_date=origin_date)
    if not data:
        raise HTTPException(status_code=404, detail="Observation data unavailable.")
    return data


@router.get("/horizon-diagnostics/{station_id}", response_model=HorizonDiagnosticsResponse)
def get_diagnostics(
    station_id: str,
    mode: str = Query(default="historical_holdout_replay", description="'historical_holdout_replay' or 'operational_current'"),
    origin_date: Optional[str] = Query(default=None, description="Optional explicit origin date (YYYY-MM-DD)"),
):
    """Retrieves full horizon diagnostic audit data for H1 through H12 (Section 24)."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    data = get_horizon_diagnostics(station_id, mode=mode, origin_date=origin_date)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to run horizon diagnostics.")
    return data


