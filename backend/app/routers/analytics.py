"""Historical Analytics router."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.analytics import (
    AnalyticsSummary,
    HistoricalTimeSeriesResponse,
    ScopedObservationsResponse,
)
from backend.app.services.data_service import (
    get_station_by_id,
    get_station_analytics,
    get_station_timeseries,
    get_scoped_observations,
    get_scoped_timeseries,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary/{station_id}", response_model=AnalyticsSummary)
def get_analytics_summary(station_id: str):
    """Retrieves authoritative historical summary statistics for a station."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    summary = get_station_analytics(station_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Historical records not found for station.")
    return summary


@router.get("/timeseries/{station_id}", response_model=HistoricalTimeSeriesResponse)
def get_analytics_timeseries(station_id: str, limit: int = Query(default=365, ge=1, le=3650)):
    """Retrieves chronological observations for a station up to limit."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    series = get_station_timeseries(station_id, limit=limit)
    return {
        "station_id": station_id,
        "total_points": len(series),
        "data": series,
    }


@router.get("/observations", response_model=ScopedObservationsResponse)
def get_observations(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    station_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=5000),
):
    """Retrieves canonical observations scoped to state, district, or station (sorted descending)."""
    records = get_scoped_observations(state=state, district=district, station_id=station_id, limit=limit)
    return {
        "scope": {
            "state": state,
            "district": district,
            "station_id": station_id,
        },
        "total_records": len(records),
        "data": records,
    }


@router.get("/scoped-timeseries")
def get_scoped_analytics_timeseries(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    station_id: Optional[str] = Query(default=None),
    limit: int = Query(default=365, ge=1, le=3650),
):
    """Retrieves chronological observations or aggregated daily timeseries for state/district/station."""
    series = get_scoped_timeseries(state=state, district=district, station_id=station_id, limit=limit)
    return {
        "scope": {
            "state": state,
            "district": district,
            "station_id": station_id,
        },
        "total_points": len(series),
        "data": series,
    }


@router.get("/station-history/{station_id}")
def get_station_history(station_id: str, limit: int = Query(default=30, ge=1, le=365)):
    """Retrieves recent canonical observations for Station Explorer (sorted descending)."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    records = get_scoped_observations(station_id=station_id, limit=limit)
    return {
        "station_id": station_id,
        "total_records": len(records),
        "data": records,
    }
